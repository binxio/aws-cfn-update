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
import sys
import os.path
import json
import collections
from typing import Any, TextIO

from ruamel.yaml import YAML


class CfnUpdater(object):
    """
    base class for a CloudFormation  update. To implement a specific updater:

    - inherit this class
    - override the method update_template()
    - call the method update(path)

    it will read the template from files with extension .yaml, .yml and .json into
    the property `self.template`.

    If the property `self.dirty` is set to True, the template will be written
    back to the originating file.

    Please note that formatting and comments may be lost, when using this
    updater.
    """

    def __init__(self):
        self.basename = None
        self.template = False
        self.template = None
        self.template_format = None
        self.dirty = False
        self.dry_run = False
        self.verbose = False
        self._filename = None
        self.yaml = CustomYAML(typ="rt")
        self.yaml.preserve_quotes = True
        self.yaml.explicit_start = True
        self.yaml.width = 4096
        self.yaml.indent(mapping=2, sequence=4, offset=2)

    def override_yaml_dump(self):
        self._original_yaml_dump = self.yaml.dump

        def _dump_with_transform(self, data, stream=None, **kw):
            if "transform" not in kw:
                kw["transform"] = _sequence_indent_two
            return self._orig_dump(data, stream, **kw)

        ruamel.yaml.YAML.dump = _dump_with_transform

    @property
    def filename(self):
        """
        current template filename
        """
        return self._filename

    @filename.setter
    def filename(self, filename):
        """
        requires `filename` ends with `.json`, `.yaml` or `.yml`.
        sets `basename`, `template_format` and `_filename` accordingly.
        clears `dirty` and `templae`
        """
        self._filename = filename
        parts = os.path.splitext(os.path.basename(filename))
        self.basename = parts[0]
        self.template_format = parts[1]
        self.template = None
        self.dirty = False
        if self.template_format not in (".json", ".yml", ".yaml"):
            raise ValueError("%s has no .json, .yaml or .yml extension." % filename)

    def load(self):
        """
        loads `template` from `filename` as dictionary.
        """
        self.dirty = False
        self.template = None
        with open(self.filename, "r") as f:
            if self.template_format == ".json":
                self.template = json.load(f, object_pairs_hook=collections.OrderedDict)
            else:
                self.template = self.yaml.load(f)

    def is_cloudformation_template(self):
        """
        returns true if the `self.template` is a AWS CloudFormation template
        """
        return self.template and "AWSTemplateFormatVersion" in self.template

    def write(self):
        """
        write modified content from `template` to `filename`. It will retain it's original
        format (yaml or json) but loose original formatting and comments.
        """
        if not self.dirty:
            if self.verbose:
                sys.stderr.write("INFO: no changes in {}\n".format(self.filename))
            return

        if self.dry_run:
            return

        with open(self.filename, "w") as f:
            if self.template_format == ".yaml":
                self.yaml.dump(self.template, f)
            else:
                json.dump(self.template, f, separators=(",", ": "), indent=2)

    def update_template(self):
        """
        implement the update logic of `self.template`. Set self.dirty to True, if you modified.
        """
        pass

    @property
    def resources(self):
        return self.template.get("Resources", {})

    def update(self, path):
        """
        recursively updates all the cloudformation templates in the specified `path`. `path` may be a file,
        a directory or a list of paths.
        """
        if isinstance(path, (list, tuple)):
            for p in path:
                self.update(p)
        elif os.path.isfile(path):
            if (
                path.endswith(".yml")
                or path.endswith(".yaml")
                or path.endswith(".json")
            ):
                self.filename = path
                self.load()
                if self.is_cloudformation_template():
                    self.update_template()
                    self.write()
                else:
                    if self.verbose:
                        sys.stderr.write(
                            "INFO: skipping {} as it is not a CloudFormation template\n".format(
                                path
                            )
                        )
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    self.update(os.path.join(root, f))
        else:
            sys.stderr.write("ERROR: {} is not a file or directory\n".format(path))
            sys.exit(1)


def read_template(filename: str) -> dict:
    src = CfnUpdater()
    src.filename = filename
    src.load()
    return src.template


def _standardize_multi_sequence_indent(line: str) -> str:
    """
    >>> _standardize_multi_sequence_indent("    -    -    - a  ")
    '    - - - a  '
    """
    offset = 0
    dashes = 0
    preamble = 0
    while offset < len(line) and line[offset] == " ":
        offset += 1
        preamble += 1

    while offset < len(line) and line[offset] in [" ", "-"]:
        if line[offset] == "-":
            dashes += 1
        offset += 1

    if not offset:
        return line

    return " " * preamble + "- " * dashes + line[offset:]


def _sequence_indent_two(s):
    """
    indent nested sequences to multiples of 2 spaces. ruamel.yaml with the identing (2,4,2)
    indents only the first sequence with two spaces, nested sequences are indented with 4 spaces.

    # >>> _sequence_indent_two('- a\\n- b\\n- c\\n')
    # '- a\\n- b\\n- c\\n'
    # >>> _sequence_indent_two('- a\\n  - b\\n  - c\\n')
    # '- a\\n  - b\\n  - c\\n'
    >>> _sequence_indent_two('- a\\n    - b\\n    - c\\n')
    '- a\\n  - b\\n  - c\\n'

    # >>> _sequence_indent_two('- a\\n    - b\\n        - A\\n        - B\\n')
    # '- a\\n  - b\\n    - A\\n    - B\\n'
    # >>> _sequence_indent_two('- a\\n    - b\\n    -    - A\\n        - B\\n        - C\\n')
    # '- a\\n  - b\\n  - - A\\n      - B\\n      - C\\n'
    # >>> _sequence_indent_two('-    -     - a\\n           - b\\n           - c\\n           - d\\n     -     - c\\n           - d\\n           - c\\n')
    # '- - - a\\n    - b\\n    - c\\n    - d\\n  - - c\\n    - d\\n    - c\\n'
    """
    result = []
    first_indent = -1
    for line in s.splitlines(keepends=True):
        indent_level = len(line) - len(line.lstrip())
        if indent_level < len(line) and line[indent_level] == '-' and not line.startswith('---'):
            line = _standardize_multi_sequence_indent(line)
            if first_indent == -1:
                first_indent = indent_level
            extra_indent = indent_level - first_indent
            if extra_indent > 2:
                line = " " * (first_indent + int(extra_indent/4)*2) + line.lstrip()
        else:
            first_indent = -1

        result.append(line)

    return "".join(result)


class CustomYAML(YAML):
    """
    overrides to dump method to correct indentation of nested sequences to multiples of 2 spaces.
    """

    def dump(self, data, stream=None, **kw):
        if "transform" not in kw:
            kw["transform"] = _sequence_indent_two
        return super().dump(data, stream, **kw)
