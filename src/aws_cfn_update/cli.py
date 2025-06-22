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
import os
import re
import shutil
import sys
from copy import copy
from datetime import datetime
from aws_cfn_update.packer_ami_updater import main as packer_latest_ami

import click
import pytz

from aws_cfn_update.config_rule_inline_code_updater import ConfigRuleInlineCodeUpdater
from aws_cfn_update.container_image_updater import ContainerImageUpdater
from aws_cfn_update.cron_schedule_expression_updater import (
    CronScheduleExpressionUpdater,
)
from aws_cfn_update.latest_ami_updater import AMIUpdater
from aws_cfn_update.rest_api_body_updater import RestAPIBodyUpdater
from aws_cfn_update.lambda_inline_code_updater import LambdaInlineCodeUpdater
from aws_cfn_update.lambda_s3_key_updater import LambdaS3KeyUpdater
from aws_cfn_update.statemachine_updater import update_state_machine_definition
from aws_cfn_update.remove_resource import remove_resource
from aws_cfn_update.add_new_resources import add_new_resources
from aws_cfn_update.oidc_provider_thumbprints_updater import (
    update_oidc_provider_thumbprint,
)


@click.group()
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="do not change anything, just show what is going to happen",
)
@click.option("--verbose", is_flag=True, default=False, help="show more output")
@click.pass_context
def cli(ctx, dry_run, verbose):
    """Programmatically update CloudFormation templates"""
    ctx.obj = copy(ctx.params)


def validate_image(ctx, param, value):
    if all(map(lambda i: re.match(r"(?:.+/)?([^:]+)(?::.+)?", i), value)):
        return value
    else:
        raise click.BadParameter(
            '"{}" is not a valid docker image specification'.format(value)
        )


@cli.command(name="container-image", help=ContainerImageUpdater.__doc__)
@click.option(
    "--image",
    required=False,
    multiple=True,
    default=[],
    callback=validate_image,
    help="to update to",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def task_image(ctx, image, path):
    if not image:
        image = os.getenv("AWS_CFN_UPDATE_CONTAINER_IMAGES", "").split()

    if not image:
        click.echo("no container images to update")
        return

    updater = ContainerImageUpdater()
    updater.main(image, ctx.obj["dry_run"], ctx.obj["verbose"], list(path))


@cli.command(name="latest-ami", help=AMIUpdater.__doc__)
@click.option(
    "--ami-name-pattern",
    required=True,
    help="glob style pattern of the AMI image name to use",
)
@click.option(
    "--add-new-version",
    is_flag=True,
    default=False,
    help="of the AMI resource and replace all references",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def ami_image_update(ctx, ami_name_pattern, add_new_version, path):
    updater = AMIUpdater()
    updater.main(
        ami_name_pattern,
        ctx.obj["dry_run"],
        ctx.obj["verbose"],
        add_new_version,
        list(path),
    )


@cli.command(
    name="cron-schedule-expression", help=CronScheduleExpressionUpdater.__doc__
)
@click.option(
    "--timezone",
    required=False,
    help="to use to calculate the UTC time",
    default="Europe/Amsterdam",
)
@click.option(
    "--date",
    type=click.DateTime(),
    default=datetime.now(),
    help="to use as reference date",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def cron_schedule_expression(ctx, timezone, date, path):
    updater = CronScheduleExpressionUpdater()
    try:
        tz = pytz.timezone(timezone)
        updater.main(tz, date, ctx.obj["dry_run"], ctx.obj["verbose"], list(path))
    except pytz.exceptions.UnknownTimeZoneError:
        raise click.BadParameter(
            "invalid timezone specified", ctx=ctx, param="timezone"
        )


@cli.command(name="rest-api-body", help=RestAPIBodyUpdater.__doc__)
@click.option(
    "--resource", required=True, help="AWS::ApiGateway::RestApi body to update"
)
@click.option(
    "--open-api-specification",
    required=True,
    type=click.Path(exists=True),
    help="defining the interface",
)
@click.option(
    "--api-gateway-extensions",
    required=True,
    type=click.Path(exists=True),
    help="to add the the specification",
)
@click.option(
    "--add-new-version",
    is_flag=True,
    default=False,
    help="of the RestAPI resource and replace all references",
)
@click.option(
    "--keep",
    default=1,
    help="number of versions to keep, if --add-new-version is specified",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def swagger_document(
    ctx,
    resource,
    open_api_specification,
    api_gateway_extensions,
    path,
    add_new_version,
    keep,
):
    updater = RestAPIBodyUpdater()
    updater.main(
        resource,
        open_api_specification,
        api_gateway_extensions,
        list(path),
        add_new_version,
        keep,
        ctx.obj["dry_run"],
        ctx.obj["verbose"],
    )


@cli.command(name="lambda-inline-code", help=LambdaInlineCodeUpdater.__doc__)
@click.option(
    "--resource", required=True, help="name of the AWS::Lambda::Function to update"
)
@click.option(
    "--file", required=True, type=click.Path(exists=True), help="containing the source"
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def lambda_body(ctx, resource, file, path):
    updater = LambdaInlineCodeUpdater()

    with open(file, "r") as f:
        body = f.read()
    updater.main(resource, body, list(path), ctx.obj["dry_run"], ctx.obj["verbose"])


@cli.command(name="lambda-s3-key", help=LambdaS3KeyUpdater.__doc__)
@click.option(
    "--s3-key",
    required=False,
    multiple=True,
    default=[],
    help="The new S3 key in semver format",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def update_s3_key(ctx, s3_key, path):
    updater = LambdaS3KeyUpdater()
    if not s3_key:
        s3_key = os.getenv("AWS_CFN_UPDATE_LAMBDA_S3_KEYS", "").split()

    if not s3_key:
        click.echo("no Lambda s3 keys to update")
        return

    updater.main(s3_key, list(path), ctx.obj["dry_run"], ctx.obj["verbose"])


@cli.command(name="config-rule-inline-code", help=ConfigRuleInlineCodeUpdater.__doc__)
@click.option("--resource", required=True, help="name of the AWS::Config::ConfigRule")
@click.option(
    "--file", required=True, type=click.Path(exists=True), help="containing the source"
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def config_rule_body(ctx, resource, file, path):
    updater = ConfigRuleInlineCodeUpdater()

    with open(file, "r") as f:
        body = f.read()
    updater.main(resource, body, list(path), ctx.obj["dry_run"], ctx.obj["verbose"])


cli.add_command(update_state_machine_definition)
cli.add_command(remove_resource)
cli.add_command(add_new_resources)
cli.add_command(packer_latest_ami)
cli.add_command(update_oidc_provider_thumbprint)


def main():
    width = shutil.get_terminal_size().columns if sys.stdout.isatty() else 255
    cli(terminal_width=width, max_content_width=width - 5)


if __name__ == "__main__":
    main()
