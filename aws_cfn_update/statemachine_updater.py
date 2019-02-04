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
import json
import sys
import click

from aws_cfn_update.cfn_updater import CfnUpdater

class StateMachineDefinitionUpdater(CfnUpdater):
    """
    Updates the definition of an AWS::StepFunctions::StateMachine.
    """

    def __init__(self):
        super(StateMachineDefinitionUpdater, self).__init__()
        self.resource_name = None
        self.definition = None
        self.definition_file = None
        self.template = None
        self.verbose = False
        self.dry_run = False

    def update_template(self):
        """
        updates the Definition of Step Function StateMachine.
        """
        resources = self.template.get('Resources', {})
        for name, resource in filter(lambda k,v: k == self.resource_name, enumerate(resources)):
            if 'Properties' not in resource:
                resource['Properties'] = {}

            definition = resource['Properties'].get('DefinitionString')
            if definition != self.definition:
                    sys.stderr.write(
                        'INFO: updating definition of state machine {} with {}\n'.format(self.resource_name,
                                                                                         self.definition_file))
                    resource['Properties']['DefinitionString'] = self.definition
                    self.dirty = True

    def read_definition(self):
        with open(self.definition_file, 'r') as f:
            self.definition = json.load(f)

    def main(self, resource_name, definition_file, path, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self.resource_name = resource_name
        self.definition_file = definition_file
        self.read_definition()
        self.update(path)


@click.command(name='state-machine-definition', help=StateMachineDefinitionUpdater.__doc__)
@click.option('--resource', required=True, help='AWS::StepFunctions::StateMachine definition to update')
@click.option('--definition', required=True, type=click.Path(exists=True), help='of the state machine')
@click.argument('path', nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def update_state_machine_definition(ctx, resource, definition, path):
    updater = StateMachineDefinitionUpdater()
    updater.main(resource, definition, path, ctx.obj['dry_run'], ctx.obj['verbose'])