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
import difflib
import re
import sys
from io import BytesIO
from io import StringIO

import jsonmerge
from ruamel.yaml import YAML

from aws_cfn_update.cfn_updater import CfnUpdater
from aws_cfn_update.replace_references import replace_references


class RestAPIBodyUpdater(CfnUpdater):
    """
    Updates the body of a REST API Resource, with an standard Open API
    specification merged with AWS API Gateway extensions.

    If you specify --add-new-version, it will create a new
    version of the resource and update all references
    to it. This will enforce the deployment of the new api.

    If you want to keep the previous definition, specify --keep to
    a value of 2 or higher. This might be handy if you have old clients
    still accessing the old version of the API.

    If no changes are detected, no changes are made. Please make
    sure that all dictionary keys in th specifications are strings,
    not integers (especially the case with `responses`).
    When updating json CFN templates, the compare algorithm does
    not work properly.
    """

    def __init__(self):
        super(RestAPIBodyUpdater, self).__init__()
        self.resource_name = None
        self.open_api_specification = None
        self.api_gateway_extensions = None
        self.template = None
        self.add_new_version = False
        self.verbose = False
        self.dry_run = False
        self.keep = 1
        self.yaml = YAML()
        self._body = {}

    def load_and_merge_swagger_body(self):
        with open(self.open_api_specification, "r") as f:
            body = self.yaml.load(f)
        with open(self.api_gateway_extensions, "r") as f:
            extensions = self.yaml.load(f)

        self.body = jsonmerge.merge(body, extensions)

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self._body = body
        self.body_as_string = self.yaml_dump_to_str(self.body) if body else ""

    def yaml_dump_to_str(self, dict):
        s = StringIO()
        self.yaml.dump(dict, s)
        return s.getvalue()

    def resource_name_pattern(self):
        return re.compile(
            "^(?P<basename>{})(v(?P<version>[0-9]+))?$".format(self.resource_name)
        )

    def find_matching_resources(self):
        """
        find all resources matching the pattern `<resource_name>v[0-9]+`, sort listed
        """
        pattern = self.resource_name_pattern()

        result = []
        resources = self.template["Resources"] if "Resources" in self.template else None
        if resources:
            result = list(
                filter(
                    lambda name: "Type" in resources[name]
                    and resources[name]["Type"] == "AWS::ApiGateway::RestApi",
                    filter(lambda name: pattern.match(name), resources),
                )
            )
            result.sort(
                key=lambda n: int(pattern.match(n).group("version"))
                if pattern.match(n).group("version")
                else -1
            )
        return result

    def new_resource_name(self, name):
        match = self.resource_name_pattern().match(name)
        version = int(match.group("version")) if match.group("version") else 0
        return "{}v{}".format(match.group("basename"), version + 1)

    def copy_resource(self, resource):
        """
        Copy the resource using dump and reload. dictionary deepcopy() did not work on yaml dictionaries.
        """
        bytes = BytesIO()
        self.yaml.dump(resource, bytes)
        bytes.seek(0)
        result = self.yaml.load(bytes)
        return result

    def update_template(self):
        resources = self.find_matching_resources()
        if not resources:
            return

        name = resources[-1]
        rest_api_gateway = self.template["Resources"][name]
        current_body = rest_api_gateway.get("Properties", {}).get("Body", {})

        current_body_as_string = (
            self.yaml_dump_to_str(current_body) if current_body else ""
        )
        if self.body_as_string != current_body_as_string:
            if self.verbose:
                for text in difflib.unified_diff(
                    current_body_as_string.split("\n"), self.body_as_string.split("\n")
                ):
                    if text[:3] not in ["---", "+++"]:
                        sys.stderr.write("{}\n".format(text))

            rest_api_gateway = self.copy_resource(rest_api_gateway)
            if not "Properties" in rest_api_gateway:
                rest_api_gateway["Properties"] = {}

            rest_api_gateway["Properties"]["Body"] = self.body

            if self.add_new_version:
                new_name = self.new_resource_name(name)
                sys.stderr.write(
                    "INFO: adding resource {} with new swagger body in template {}\n".format(
                        new_name, self.filename
                    )
                )
            else:
                new_name = name
                sys.stderr.write(
                    "INFO: updating resource {} with swagger body in template {}\n".format(
                        new_name, self.filename
                    )
                )

            if self.add_new_version:
                replace_references(self.template, name, new_name)
                for i in range(0, len(resources) - (self.keep - 1)):
                    sys.stderr.write(
                        "INFO: removing resource {} from template {}\n".format(
                            resources[i], self.filename
                        )
                    )
                    del self.template["Resources"][resources[i]]
            self.template["Resources"][new_name] = rest_api_gateway

            self.dirty = True
        else:
            sys.stderr.write(
                "INFO: no changes of swagger body of {} in template {}\n".format(
                    self.resource_name, self.filename
                )
            )

    def main(
        self,
        resource_name,
        open_api_specification,
        api_gateway_extensions,
        path,
        add_new_version,
        keep,
        dry_run,
        verbose,
    ):
        self.dry_run = dry_run
        self.verbose = verbose
        self.resource_name = resource_name
        self.open_api_specification = open_api_specification
        self.api_gateway_extensions = api_gateway_extensions
        self.add_new_version = add_new_version
        self.keep = keep if keep > 0 else 1
        self.load_and_merge_swagger_body()
        self.update(path)
