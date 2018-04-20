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
import re
from copy import copy

import click

from aws_cfn_update.latest_ami_updater import AMIUpdater
from aws_cfn_update.container_image_updater import ContainerImageUpdater



@click.group()
@click.option('--dry-run', is_flag=True, default=False,
              help='do not change anything, just show what is going to happen')
@click.option('--verbose', is_flag=True, default=False, help='show more output')
@click.pass_context
def cli(ctx, dry_run, verbose):
    """Programmatically update CloudFormation templates"""
    ctx.obj = copy(ctx.params)


def validate_image(ctx, param, value):
    if re.match(r'(?:.+/)?([^:]+)(?::.+)?', value):
        return value
    else:
        raise click.BadParameter('"{}" is not a valid docker image specification'.format(value))


@cli.command(name='container-image', help=ContainerImageUpdater.__doc__)
@click.option('--image', required=True, callback=validate_image, help='to update to')
@click.argument('path', nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def task_image(ctx, image, path):
    updater = ContainerImageUpdater()
    updater.main(image, ctx.obj['dry_run'], ctx.obj['verbose'], list(path))


@cli.command(name='latest-ami', help=AMIUpdater.__doc__)
@click.option('--ami-name-pattern', required=True, help='glob style pattern of the AMI image name to use')
@click.argument('path', nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def ami_image_update(ctx, ami_name_pattern, path):
    updater = AMIUpdater()
    updater.main(ami_name_pattern, ctx.obj['dry_run'], ctx.obj['verbose'], list(path))


def main():
    cli()


if __name__ == '__main__':
    main()
