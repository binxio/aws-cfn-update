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
import copy
import fnmatch
import re
from collections import OrderedDict

import boto3
import sys

from .cfn_updater import CfnUpdater
from .replace_references import replace_references


def split_resource_name(resource_name):
    m = re.match(r"^(?P<base>.*)v(?P<version>[0-9]+)$", resource_name)

    if m is not None:
        base = m.group("base")
        version = int(m.group("version"))
    else:
        base = resource_name
        version = 0

    return base, version


def make_new_resource_name(resource_name):
    base, version = split_resource_name(resource_name)
    return "{}v{}".format(base, version + 1)


class AMIUpdater(CfnUpdater):
    """
        Updates the AMI name of Custom::AMI resources to the latest version.
        With an ami-name-pattern of `amzn-ami-*ecs-optimized` it will update
        the following resource definition from:

    \b
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.a-amazon-ecs-optimized
               Owners:
                 - amazon

        to:

    \b
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.l-amazon-ecs-optimized
               Owners:
                 - amazon


        By specifying --add-new-version, a new Custom::AMI will be added
        to the template with a new name. A suffix `v<version>` is appended
        to create the new resource. Any reference to the highest Custom::AMI version
        resource is replaced. It will change:

    \b
          CustomAMI:
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.a-amazon-ecs-optimized
               Owners:
                 - amazon
          CustomAMIv2:
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.b-amazon-ecs-optimized
               Owners:
                 - amazon
          Instance:
             Type: AWS::EC2::Instance
             Properties:
                ImageId: !Ref CustomAMI

        to:

    \b
          CustomAMI:
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.a-amazon-ecs-optimized
               Owners:
                 - amazon
          CustomAMIv2:
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.b-amazon-ecs-optimized
               Owners:
                 - amazon
          CustomAMIv3:
             Type: Custom::AMI
             Properties:
               Filters:
                 name: amzn-ami-2017.09.l-amazon-ecs-optimized
               Owners:
                 - amazon
          Instance:
             Type: AWS::EC2::Instance
             Properties:
                ImageId: !Ref CustomAMIv3
    """

    def __init__(self):
        super(AMIUpdater, self).__init__()
        self._ami_name_pattern = None
        self.add_new_version = False
        self.latest_ami_name_pattern = None

    @property
    def ami_name_pattern(self):
        return self._ami_name_pattern

    @ami_name_pattern.setter
    def ami_name_pattern(self, name):
        self._ami_name_pattern = name

    @staticmethod
    def is_ami_definition(resource):
        return resource.get("Type", "") == "Custom::AMI"

    def create_describe_image_request(self, ami):
        # copy the filters values, except for name and state.
        properties = ami.get("Properties", {})
        filters = [
            {"Name": "name", "Values": [self.ami_name_pattern]},
            {"Name": "state", "Values": ["available"]},
        ]
        for k, v in properties.get("Filters", {}).items():
            if k not in ["name", "state"]:
                filters.append({"Name": k, "Values": v if isinstance(v, list) else [v]})

        # copy the rest of the arguments
        result = {
            n: (
                properties.get(n)
                if isinstance(properties.get(n), list)
                else [properties.get(n)]
            )
            for n in filter(
                lambda n: properties.get(n) is not None,
                ["Owners", "ImageIds", "ExecutableUsers"],
            )
        }
        result["Filters"] = filters
        return result

    def _describe_images(self, **kwargs):
        return boto3.client("ec2").describe_images(**kwargs)

    def load_latest_ami_name_pattern(self, resource):
        response = self._describe_images(**self.create_describe_image_request(resource))

        images = sorted(response["Images"], key=lambda i: i["CreationDate"])
        self.latest_ami_name_pattern = images[-1]["Name"] if len(images) > 0 else None
        if len(images) > 0:
            sys.stderr.write(
                "INFO: using {} matching {}, created on {}\n".format(
                    self.latest_ami_name_pattern,
                    self.ami_name_pattern,
                    images[-1]["CreationDate"],
                )
            )

    def is_ami_name_pattern_match(self, name):
        regex = re.compile(fnmatch.translate(self.ami_name_pattern))
        return regex.match(name)

    def all_custom_ami_resources(self):
        r = self.resources
        return filter(
            lambda n: self.is_ami_definition(r[n]) and self.is_name_filter_match(r[n]),
            r,
        )

    def is_name_filter_match(self, ami):
        if (
            "Properties" in ami
            and "Filters" in ami["Properties"]
            and "name" in ami["Properties"]["Filters"]
        ):
            return self.is_ami_name_pattern_match(ami["Properties"]["Filters"]["name"])
        return False

    def custom_ami_resources_partitions(self):
        partitions = {}
        ami_resources = self.all_custom_ami_resources()
        for resource_name in ami_resources:
            base, _ = split_resource_name(resource_name)
            if base not in partitions:
                partitions[base] = {}
            partitions[base][resource_name] = self.resources[resource_name]

        for base in partitions:
            resource_names = sorted(
                partitions[base].keys(), key=lambda n: split_resource_name(n)[1]
            )
            yield OrderedDict({name: partitions[base][name] for name in resource_names})

    @staticmethod
    def latest_custom_ami_resource(ami_resources):
        result = None
        highest_version = -1
        for resource_name in ami_resources:
            _, version = split_resource_name(resource_name)
            if version > highest_version:
                result = resource_name
                highest_version = version

        return result

    def ami_requires_update(self, ami):
        name = ami["Properties"]["Filters"]["name"]
        return (
            self.latest_ami_name_pattern is not None
            and name != self.latest_ami_name_pattern
        )

    def update_ami(self, resource_name, ami):
        if self.ami_requires_update(ami):
            ami["Properties"]["Filters"]["name"] = self.latest_ami_name_pattern
            sys.stderr.write(
                'INFO: updating AMI definition "{}" name filter to {} in {}\n'.format(
                    resource_name, self.latest_ami_name_pattern, self.filename
                )
            )
            self.dirty = True
        else:
            if self.verbose:
                sys.stderr.write(
                    'INFO: AMI definition "{}" name already up to date in {}\n'.format(
                        resource_name, self.filename
                    )
                )

    def update_inplace(self):
        """
        updates the name filter of AMI resource definitions in `self.template`.
        """
        for resource_name in self.all_custom_ami_resources():
            ami = self.resources[resource_name]
            self.load_latest_ami_name_pattern(ami)
            self.update_ami(resource_name, ami)

    def add_new_ami_resource(self):
        """
        add a new version of the AMI resource definition in `self.template`.
        """
        for ami_resources in self.custom_ami_resources_partitions():
            resource_name = self.latest_custom_ami_resource(ami_resources)
            if resource_name is not None:
                ami = copy.deepcopy(self.resources[resource_name])
                self.load_latest_ami_name_pattern(ami)
                if self.ami_requires_update(ami):
                    new_resource_name = make_new_resource_name(resource_name)
                    self.resources[new_resource_name] = ami
                    self.update_ami(new_resource_name, ami)
                    for old_resource_name in reversed(ami_resources):
                        if replace_references(
                            self.template, old_resource_name, new_resource_name
                        ):
                            break

    def update_template(self):
        if self.add_new_version:
            self.add_new_ami_resource()
        else:
            self.update_inplace()

    def main(self, ami_name_pattern, dry_run, verbose, add_new_version, path):
        self.dry_run = dry_run
        self.verbose = verbose
        self.ami_name_pattern = ami_name_pattern
        self.add_new_version = add_new_version
        self.load_latest_ami_name_pattern({})
        if self.latest_ami_name_pattern is None:
            sys.stderr.write(
                "ERROR: image name {} does not resolve to an active AMI \n".format(
                    self.ami_name_pattern
                )
            )
            sys.exit(1)

        self.update(path)
