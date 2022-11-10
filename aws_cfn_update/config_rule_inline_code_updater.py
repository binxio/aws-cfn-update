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
from ruamel.yaml.scalarstring import PreservedScalarString


class ConfigRuleInlineCodeUpdater(CfnUpdater):
    """
    Updates the inline code of an AWS::Config::ConfigRule resource.

\b
  ConfigRule:
    Type: AWS::Config::ConfigRule

\b
  ConfigRule:
    Type: AWS::Config::ConfigRule
    Properties:
      Source:
        Owner: CUSTOM_POLICY
        CustomPolicyDetails:
          EnableDebugLogDelivery: true
          PolicyRuntime: guard-2.x.x
          PolicyText: |-
            rule name when resourceType == "AWS::S3::Bucket" {
                ...
            }
          ...
    """

    def __init__(self):
        super(ConfigRuleInlineCodeUpdater, self).__init__()
        self._image = []

    def update_template(self):
        """
        updates the Code property of a AWS::Lambda::Function resource of name `self.resource` to `self.code`
        """
        resource = self.template.get('Resources', {}).get(self.resource, None)
        if resource and resource['Type'] == 'AWS::Config::ConfigRule':
            properties = resource.get('Properties', {})
            source = properties.get('Source', {})
            details = source.get('CustomPolicyDetails', {})
            old_code = details.get('PolicyText', None)

            if old_code != self.code:
                sys.stderr.write(
                    'INFO: updating inline code of lambda {} in {}\n'.format(self.resource, self.filename))
                if 'Properties' not in resource:
                    resource['Properties'] = {}
                if 'Source' not in resource['Properties']:
                    resource['Properties']['Source'] = {}
                if 'CustomPolicyDetails' not in resource['Properties']['Source']:
                    resource['Properties']['Source']['CustomPolicyDetails'] = {}

                resource['Properties']['Source']['CustomPolicyDetails'] = {'PolicyText': PreservedScalarString(self.code)}
                self.dirty = True
        elif resource:
            sys.stderr.write(
                'WARN: resource {} in {} is not of type AWS::Lambda::Function\n'.format(self.resource, self.filename))

    def main(self, resource, code, paths, dry_run, verbose):
        self.resource = resource
        self.code = code
        self.dry_run = dry_run
        self.verbose = verbose
        self.update(paths)
