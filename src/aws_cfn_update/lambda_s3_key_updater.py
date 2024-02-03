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
#   Copyright 2024 binx.io B.V.
import re
import sys
from typing import Optional

from .cfn_updater import CfnUpdater

_s3_key_semver_pattern = re.compile(
    r"(.*)(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?\.zip$"
)


class LambdaS3KeyUpdater(CfnUpdater):
    """
        Updates the S3Key entry of a Lambda Function definition. The s3 key should
        match the pattern <prefix><semver>.zip.

    \b
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function
        Properties:
          Code:
            S3Bucket: !Sub 'binxio-public-${AWS::Region}'
            S3Key: lambdas/iam-sudo-0.1.0.zip
    \b
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function
        Properties:
          Code:
            S3Bucket: !Sub 'binxio-public-${AWS::Region}'
            S3Key: lambdas/iam-sudo-0.3.1.zip
              ...

        The environment variable AWS_CFN_UPDATE_LAMBDA_S3_KEYS can be used to specify a
        whitespace separated list of S3 keys to update.
    """

    def __init__(self):
        super().__init__()
        self._s3_keys = {}

    @property
    def s3_keys(self) -> [str]:
        return self._s3_keys.values()

    def s3_key_by_prefix(self, prefix: str) -> Optional[str]:
        return self._s3_keys.get(prefix)

    @s3_keys.setter
    def s3_keys(self, s3_keys: [str]):
        self._s3_keys = {}
        for s3_key in s3_keys:
            match = _s3_key_semver_pattern.match(s3_key)
            if not match:
                raise ValueError(f"{s3_key} is not a semver S3Key")
            self._s3_keys[match.group(1)] = s3_key

    def update_template(self):
        """
        updates the S3Key property of a AWS::Lambda::Function definition.

        """
        for resource_name, resource in self.template.get("Resources", {}).items():
            if resource and resource["Type"] == "AWS::Lambda::Function":
                code = resource.get("Properties", {}).get("Code", {})
                s3_key = code.get("S3Key")
                if not s3_key:
                    return

                match = _s3_key_semver_pattern.match(s3_key)
                if match and (replacement := self.s3_key_by_prefix(match.group(1))):
                    if replacement != s3_key:
                        sys.stderr.write(
                            "INFO: updating S3Key of Lambda function {} in {}\n".format(
                                resource_name, self.filename
                            )
                        )

                        code["S3Key"] = replacement
                        self.dirty = True

    def main(self, s3_keys: [str], paths, dry_run, verbose):
        self.s3_keys = s3_keys
        self.dry_run = dry_run
        self.verbose = verbose
        self.update(paths)
