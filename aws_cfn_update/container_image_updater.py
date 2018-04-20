#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Copyright 2018 binx.io B.V.
import sys
from .cfn_updater import CfnUpdater


class ContainerImageUpdater(CfnUpdater):
    """
    Updates the Docker image of ECS Container Definitions.

    it will update any container definition where the base image name matches
    the specified image name excluding the tag.

    For example, an image name of `mvanholsteijn/paas-monitor:0.6.0` will update:

\b
        Type: AWS::ECS::TaskDefinition
        Properties:
          ContainerDefinitions:
            - Name: paas-monitor
              Image: mvanholsteijn/paas-monitor:0.5.9

    to:

\b
        Type: AWS::ECS::TaskDefinition
        Properties:
          ContainerDefinitions:
            - Name: paas-monitor
              Image: mvanholsteijn/paas-monitor:0.6.0

    """

    def __init__(self):
        super(ContainerImageUpdater, self).__init__()
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
