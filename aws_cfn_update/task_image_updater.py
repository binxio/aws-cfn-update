import sys
from .cfn_updater import CfnUpdater


class TaskImageUpdater(CfnUpdater):
    """
    Updates the Image of ECS Container Definitions.

    it will update any container definition where the base image name matches
    the specified image name excluding the tag.

    For example, an image name of `mvanholsteijn/paas-monitor:0.6.0` will update:

        Type: AWS::ECS::TaskDefinition
        Properties:
          ContainerDefinitions:
            - Name: paas-monitor
              Image: mvanholsteijn/paas-monitor:0.5.9

    to:

        Type: AWS::ECS::TaskDefinition
        Properties:
          ContainerDefinitions:
            - Name: paas-monitor
              Image: mvanholsteijn/paas-monitor:0.6.0

    """

    def __init__(self):
        super(TaskImageUpdater, self).__init__()
        self._image = []

    @property
    def image(self):
        return ':'.join(self._image)

    @image.setter
    def image(self, image):
        self._image = image.split(':', 2) if image is not None else []

    @property
    def base_image(self):
        return self._image[0] if self._image is not None and len(self._image) > 0 else ''

    @property
    def image_tag(self):
        return self._image[1] if self._image is not None and len(self._image) > 1 else ''

    @staticmethod
    def is_task_definition(resource):
        """
        returns true if the resource is of type AWS::ECS::TaskDefinition
        """
        return resource.get('Type', '') == 'AWS::ECS::TaskDefinition'

    def is_matching_container(self, container):
        """
        returns true if there is a match on the image
        """
        return container.get('Image', '').split(':')[0] == self.base_image

    def all_matching_task_definitions(self, resources):
        return filter(lambda n: self.is_task_definition(resources[n]), resources)

    def update_template(self):
        """
        updates the Image of container definitions in the CFN template `self.template`.
        """
        resources = self.template.get('Resources', {})
        for task_name in self.all_matching_task_definitions(resources):
            task = resources[task_name]
            containers = task.get('Properties', {}).get('ContainerDefinitions', [])
            for container in filter(lambda c: self.is_matching_container(c), containers):
                if container['Image'] != self.image:
                    sys.stderr.write(
                        'INFO: updating image of container definition {} for task {} in {}\n'.format(
                            container['Name'], task_name, self.filename))
                    container['Image'] = self.image
                    self.dirty = True

    def main(self, image, dry_run, verbose, paths):
        self.image = image
        self.dry_run = dry_run
        self.verbose = verbose
        self.update(paths)
