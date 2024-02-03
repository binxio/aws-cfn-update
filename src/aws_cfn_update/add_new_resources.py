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
import click

from .add_missing_resources import add_missing_resources
from .cfn_updater import CfnUpdater, read_template


class AddNewResources(CfnUpdater):
    """
    Add resources that exist in the new template and not in the existing template.
    """

    def __init__(self):
        super(AddNewResources, self).__init__()
        self.source: dict = {}

    def update_template(self):
        self.dirty = add_missing_resources(self.template, self.source)


@click.command(name="add-new-resources", help=AddNewResources.__doc__)
@click.option(
    "--source",
    required=True,
    help="template to add resources from",
    type=click.Path(exists=True),
)
@click.argument("path", nargs=1, required=True, type=click.Path(exists=True))
@click.pass_context
def add_new_resources(ctx, source, path):
    updater = AddNewResources()
    updater.dry_run = ctx.obj["dry_run"]
    updater.verbose = ctx.obj["verbose"]
    updater.source = read_template(source)
    updater.update(path)
