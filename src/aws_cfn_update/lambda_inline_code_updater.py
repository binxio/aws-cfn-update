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


class LambdaInlineCodeUpdater(CfnUpdater):
    """
        Updates the inline code of an AWS::Lambda::Function resource.

    \b
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function

    \b
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function
        Properties:
          Code:
            ZipFile:
              import boto3
              import cfnresponse
              ELB = boto3.client('elbv2')
              ...
    """

    def __init__(self):
        super(LambdaInlineCodeUpdater, self).__init__()
        self._image = []

    def update_template(self):
        """
        updates the Code property of a AWS::Lambda::Function resource of name `self.resource` to `self.code`
        """
        resource = self.template.get("Resources", {}).get(self.resource, None)
        if resource and resource["Type"] == "AWS::Lambda::Function":
            code = resource.get("Properties", {}).get("Code", {})
            old_code = code["ZipFile"] if "ZipFile" in code else None
            if old_code != self.code:
                sys.stderr.write(
                    "INFO: updating inline code of lambda {} in {}\n".format(
                        self.resource, self.filename
                    )
                )
                if "Properties" not in resource:
                    resource["Properties"] = {}
                if "Code" not in resource["Properties"]:
                    resource["Properties"]["Code"] = {}
                resource["Properties"]["Code"] = {
                    "ZipFile": PreservedScalarString(self.code)
                }
                self.dirty = True
        elif resource:
            sys.stderr.write(
                "WARN: resource {} in {} is not of type AWS::Lambda::Function\n".format(
                    self.resource, self.filename
                )
            )

    def main(self, resource, code, paths, dry_run, verbose):
        self.resource = resource
        self.code = code
        self.dry_run = dry_run
        self.verbose = verbose
        self.update(paths)
