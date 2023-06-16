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
import fnmatch
import re
import copy
import click
import json
import boto3
from typing import List
from ruamel.yaml.comments import TaggedScalar, CommentedSeq

from .cfn_updater import CfnUpdater

import logging


def is_reference(obj, fld, name):
    if isinstance(obj, dict):
        if fld == "Ref":
            return obj["Ref"] == name
        elif fld == "FN::GetAtt":
            return len(obj[fld]) > 0 and obj[fld][0] == name
        elif fld == "FN::Sub":
            return isinstance(obj[fld], str) and references_in_sub(obj[fld], name)


def references_in_sub(sub, name):
    return list(
        filter(
            lambda n: n == name,
            map(lambda n: n.split(".")[0], re.findall(r"\${([^!][^}]*)}", sub)),
        )
    )


def is_tag_reference(obj, name):
    if isinstance(obj, TaggedScalar):
        if obj.tag.suffix == "Ref":
            return str(obj.value) == name
        elif obj.tag.suffix == "Sub":
            return references_in_sub(obj.value, name)
        elif obj.tag.suffix == "GetAtt":
            return str(obj.value).split(".")[0] == name
    elif isinstance(obj, CommentedSeq):
        if obj.tag.suffix == "GetAtt":
            return len(obj) > 1 and obj[0] == name
    return False


def remove_resource_from_template(template: dict, name: str):
    resources: dict = template.get("Resources")
    if resources and name in resources:
        resources.pop(name)
        remove_all_references(template, name)
        return True
    outputs: dict = template.get("Resources")
    if outputs and name in outputs:
        remove_all_references(template, name)
        return True
    return False

    return False


def remove_all_references(template, name):
    to_remove = {}
    for toplevel in template:
        if isinstance(template[toplevel], dict):
            to_remove[toplevel] = []

    for toplevel in to_remove:
        for obj in template[toplevel]:
            if has_reference(template[toplevel][obj], name, []):
                to_remove[toplevel].append(obj)
    for toplevel in to_remove:
        for obj in to_remove[toplevel]:
            logging.info(
                "Removing object %s from %s, as it references %s", obj, toplevel, name
            )
            template[toplevel].pop(obj)


def has_reference(obj, name, path):
    result = False
    if isinstance(obj, dict):
        for fld in obj:
            if is_reference(obj, fld, name):
                logging.info("INFO: %s to %s found in %s", fld, name, ".".join(path))
                result = True
            else:
                nested_path = path[:]
                nested_path.append(fld)
                result = result or has_reference(obj[fld], name, nested_path)
    elif isinstance(obj, TaggedScalar):
        if is_tag_reference(obj, name):
            logging.info("INFO: %s to %s found in %s", obj.tag, name, ".".join(path))
            result = True

    elif isinstance(obj, CommentedSeq):
        if is_tag_reference(obj, name):
            logging.info("INFO: %s to %s found in %s", obj.tag, name, ".".join(path))
            result = True
        else:
            for i in range(len(obj)):
                nested_path = path[:]
                nested_path.append("[%d]" % i)
                if has_reference(obj[i], name, nested_path):
                    logging.info(
                        "INFO: %s too %s found in array %s",
                        obj[i],
                        name,
                        ".".join(nested_path),
                    )
                    result = True

    elif isinstance(obj, list):
        for i in range(len(obj)):
            nested_path = path[:]
            nested_path.append("[%d]" % i)
            if has_reference(obj[i], name, nested_path):
                logging.info(
                    "INFO: Ref:%s found in array %s", name, ".".join(nested_path)
                )
                result = True

    return result


class ResourceRemover(CfnUpdater):
    """
    Removes the specified CloudFormation resource and all resources that reference it.
    """

    def __init__(self):
        super(ResourceRemover, self).__init__()
        self.resource_name = None

    def update_template(self):
        if remove_resource_from_template(self.template, self.resource_name):
            self.dirty = True


@click.command(name="remove-resource", help=ResourceRemover.__doc__)
@click.option("--resource", required=True, help="to remove from the template")
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def remove_resource(ctx, resource, path):
    updater = ResourceRemover()
    updater.dry_run = ctx.obj["dry_run"]
    updater.verbose = ctx.obj["verbose"]
    updater.resource_name = resource
    updater.update(path)
