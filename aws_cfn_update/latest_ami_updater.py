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
import fnmatch
import re
import sys

import boto3

from .cfn_updater import CfnUpdater


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

    to:

\b
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.l-amazon-ecs-optimized    
    """

    def __init__(self):
        super(AMIUpdater, self).__init__()
        self._ami_name_pattern = None
        self.latest_ami_name_pattern = None

    @property
    def ami_name_pattern(self):
        return self._ami_name_pattern

    @ami_name_pattern.setter
    def ami_name_pattern(self, name):
        self._ami_name_pattern = name
        self.load_latest_ami_name_pattern()

    @staticmethod
    def is_ami_definition(resource):
        return resource.get('Type', '') == 'Custom::AMI'

    def load_latest_ami_name_pattern(self):
        response = boto3.client('ec2').describe_images(
            Filters=[{'Name': 'name', 'Values': [self.ami_name_pattern]}, {'Name': 'state', 'Values': ['available']}])
        images = sorted(response['Images'], key=lambda i: i['CreationDate'])
        self.latest_ami_name_pattern = images[-1]['Name'] if len(images) > 0 else None
        if len(images) > 0:
            sys.stderr.write(
                'INFO: using {} matching {}, created on {}\n'.format(self.latest_ami_name_pattern,
                                                                     self.ami_name_pattern,
                                                                     images[-1]['CreationDate']))

    def is_ami_name_pattern_match(self, name):
        regex = re.compile(fnmatch.translate(self.ami_name_pattern))
        return regex.match(name)

    def all_custom_ami_resources(self, resources):
        return filter(lambda n: self.is_ami_definition(resources[n]) and self.is_name_filter_match(resources[n]),
                      resources)

    def is_name_filter_match(self, ami):
        if 'Properties' in ami and 'Filters' in ami['Properties'] and 'name' in ami['Properties']['Filters']:
            return self.is_ami_name_pattern_match(ami['Properties']['Filters']['name'])
        return False

    def update_template(self):
        """
        updates the name filter of AMI resource definitions in `self.template`.
        """
        resources = self.template.get('Resources', {})
        for resource_name in self.all_custom_ami_resources(resources):
            ami = resources[resource_name]
            name = ami['Properties']['Filters']['name']
            if name != self.latest_ami_name_pattern:
                ami['Properties']['Filters']['name'] = self.latest_ami_name_pattern
                sys.stderr.write(
                    'INFO: updating AMI definition "{}" name filter to {} in {}\n'.format(
                        resource_name, self.latest_ami_name_pattern, self.filename))
                self.dirty = True
            else:
                if self.verbose:
                    sys.stderr.write(
                        'INFO: AMI definition "{}" name already up to date in {}\n'.format(
                            resource_name, self.filename))

    def main(self, ami_name_pattern, dry_run, verbose, path):
        self.dry_run = dry_run
        self.verbose = verbose
        self.ami_name_pattern = ami_name_pattern
        if self.latest_ami_name_pattern is None:
            sys.stderr.write('ERROR: image name {} does not resolve to an active AMI \n'.format(self.ami_name_pattern))
            sys.exit(1)

        self.update(path)
