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

import jsonmerge
from ruamel.yaml import YAML

from .cfn_updater import CfnUpdater


class RestAPIBodyUpdater(CfnUpdater):
    """
    Updates the body of a REST API Resource, with an standard Open API
    specification merged with AWS API Gateway extensions.
    """
    def __init__(self):
        super(RestAPIBodyUpdater, self).__init__()
        self.resource_name = None
        self.open_api_specification = None
        self.api_gateway_extensions = None
        self.template = None
        self.verbose = False
        self.dry_run = False

    def load_and_merge_swagger_body(self):
        yaml = YAML()
        with open(self.open_api_specification, 'r') as f:
            body = yaml.load(f)
        with open(self.api_gateway_extensions, 'r') as f:
            extensions = yaml.load(f)

        return jsonmerge.merge(body, extensions)

    def update_template(self):
        rest_api_gateway = self.template['Resources'][self.resource_name] if self.resource_name in self.template[
            'Resources'] else None
        type = rest_api_gateway['Type'] if rest_api_gateway and 'Type' in rest_api_gateway else None

        if not rest_api_gateway:
            return

        if not type or type != 'AWS::ApiGateway::RestApi':
            sys.stderr.write(
                'ERROR: resource {} in template {} is not of type AWS::ApiGateway::RestApi\n'.format(self.resource_name,
                                                                                                     self.filename))
            return

        body = self.load_and_merge_swagger_body()
        current_body = rest_api_gateway['Properties']['Body'] if 'Body' in rest_api_gateway['Properties'] else {}

        if body != current_body:
            sys.stderr.write('INFO: updating swagger body of {} in template {}'.format(self.resource_name,self.filename))
            if self.dry_run:
                return
            if not 'Properties' in rest_api_gateway:
                rest_api_gateway['Properties'] = {}

            rest_api_gateway['Properties']['Body'] = body
            self.dirty = True
        else:
            sys.stderr.write('INFO: no changes of swagger body of {} in template {}'.format(self.resource_name,self.filename))


    def main(self, resource_name, open_api_specification, api_gateway_extensions, path, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self.resource_name = resource_name
        self.open_api_specification = open_api_specification
        self.api_gateway_extensions = api_gateway_extensions
        self.update(path)
