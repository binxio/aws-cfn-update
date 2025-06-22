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
from typing import Optional, Union, List

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


        The environment variable AWS_CFN_UPDATE_CONTAINER_IMAGES can be used to specify a
        whitespace separated list of container images to update.
    """

    def __init__(self):
        super(ContainerImageUpdater, self).__init__()
        self._images = {}

    @property
    def images(self) -> [str]:
        return self._images.values()

    @images.setter
    def images(self, images: [str]):
        self._images = {}
        for image in images:
            parts = image.split(":")
            if len(parts) != 2:
                raise ValueError(f"{image} is an invalid image name")
            base = parts[0]
            if base in self._images and image != self._images[base]:
                raise ValueError(f"image already defined for {base}")
            self._images[base] = image

    def get_new_image_reference(self, image: str) -> Optional[str]:
        return self._images.get(image.split(":")[0])

    @staticmethod
    def is_task_definition(resource):
        """
        returns true if the resource is of type AWS::ECS::TaskDefinition
        """
        return resource.get("Type", "") == "AWS::ECS::TaskDefinition"

    def all_matching_task_definitions(self, resources):
        return filter(lambda n: self.is_task_definition(resources[n]), resources)

    def update_template(self):
        """
        updates the Image of container definitions in the CFN template `self.template`.
        """
        resources = self.template.get("Resources", {})
        for task_name in self.all_matching_task_definitions(resources):
            task = resources[task_name]
            containers = task.get("Properties", {}).get("ContainerDefinitions", [])
            for container in filter(
                lambda c: self.get_new_image_reference(c["Image"]),
                filter(lambda c: isinstance(c.get("Image", None), str), containers),
            ):
                new_image = self.get_new_image_reference(container["Image"])
                if container["Image"] != new_image:
                    sys.stderr.write(
                        "INFO: updating image of container definition {} for task {} in {}\n".format(
                            container["Name"], task_name, self.filename
                        )
                    )
                    container["Image"] = new_image
                    self.dirty = True

    def main(self, image: [str], dry_run: bool, verbose: bool, paths: [str]):
        self.images = image
        self.dry_run = dry_run
        self.verbose = verbose
        self.update(paths)
