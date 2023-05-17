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

import click
from ruamel.yaml.scalarstring import LiteralScalarString

from aws_cfn_update.cfn_updater import CfnUpdater


class StateMachineDefinitionUpdater(CfnUpdater):
    """
    Updates the definition of an AWS::StepFunctions::StateMachine.

    The definition is read from the file specified by --definition.
    By default, the content will be passed into the Fn::Sub function to
    allow references to parameters and resource attributes in the template.

    If you do not want substitution for your definition, specify --no-fn-sub.

    """

    def __init__(self):
        super(StateMachineDefinitionUpdater, self).__init__()
        self.resource_name = None
        self._definition = None
        self.definition_file = None
        self.template = None
        self.with_fn_sub = True
        self.verbose = False
        self.dry_run = False

    def new_value(self, definition):
        if self.with_fn_sub:
            return isinstance(definition, dict) and definition.get(
                "Fn::Sub"
            ) == self.definition, {"Fn::Sub": self.definition}
        else:
            return definition == self.definition, self.definition

    def update_template(self):
        """
        updates the Definition of Step Function StateMachine.
        """
        resources = self.template.get("Resources", {})
        for name, resource in map(
            lambda n: (n, resources[n]),
            filter(lambda n: n == self.resource_name, resources),
        ):
            if "Properties" not in resource:
                resource["Properties"] = {}

            same, new_definition = self.new_value(
                resource["Properties"].get("DefinitionString")
            )
            if not same:
                sys.stderr.write(
                    "INFO: updating definition of state machine {}\n".format(
                        self.resource_name
                    )
                )
                resource["Properties"]["DefinitionString"] = new_definition
                self.dirty = True
            else:
                if self.verbose:
                    sys.stderr.write(
                        "INFO: no changes to definition of state machine {}\n".format(
                            self.resource_name
                        )
                    )

    @property
    def definition(self):
        return self._definition

    @definition.setter
    def definition(self, definition):
        self._definition = (
            LiteralScalarString(definition)
            if not isinstance(definition, LiteralScalarString)
            else definition
        )

    def read_definition(self, filename):
        self.definition_file = filename
        with open(self.definition_file, "r") as f:
            self.definition = LiteralScalarString(f.read())

    def main(self, resource_name, definition_file, with_fn_sub, path, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self.resource_name = resource_name
        self.with_fn_sub = with_fn_sub
        self.read_definition(definition_file)
        self.update(path)


@click.command(
    name="state-machine-definition", help=StateMachineDefinitionUpdater.__doc__
)
@click.option(
    "--resource",
    required=True,
    help="AWS::StepFunctions::StateMachine definition to update",
)
@click.option(
    "--definition",
    required=True,
    type=click.Path(exists=True),
    help="of the state machine",
)
@click.option(
    "--fn-sub/--no-fn-sub", required=False, default=True, help="for the definition"
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def update_state_machine_definition(ctx, resource, definition, fn_sub, path):
    updater = StateMachineDefinitionUpdater()
    updater.main(
        resource, definition, fn_sub, list(path), ctx.obj["dry_run"], ctx.obj["verbose"]
    )
