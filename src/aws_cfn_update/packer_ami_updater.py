import fnmatch
import json
import re

import boto3
import click
import sys


class PackerAMIUpdater(object):
    """
        Updates a packer.json source_ami_filter to the latest AMI version.
        With an ami-name-pattern of `Windows_Server-2016-English-Full-Base-*` it will
        update the following from:
    \b
          "source_ami_filter": {
            "filters": {
              "virtualization-type": "hvm",
              "name": ""Windows_Server-2016-English-Full-Base-2020.01.15",
              "root-device-type": "ebs"
            },
            "owners": [ "801119661308" ],
          },
    \b
        to:
    \b
          "source_ami_filter": {
            "filters": {
              "virtualization-type": "hvm",
              "name": "Windows_Server-2016-English-Full-Base-2020.02.12",
              "root-device-type": "ebs"l
            },
            "owners": [ "801119661308" ],
          },
    """

    def __init__(self):
        self.packer: dict = None
        self.filename: str = None
        self.dirty: bool = False
        self.verbose: bool = False
        self.dry_run: bool = False
        self.ami_name_pattern: str = None
        self.ec2 = boto3.client("ec2")

    def is_source_filter_name_match(self, source_ami_filter: dict) -> bool:
        name = source_ami_filter.get("filters", {}).get("name")
        pattern = re.compile(fnmatch.translate(self.ami_name_pattern))
        return pattern.match(name) if name else None

    def create_describe_image_request(self, source_ami_filter: dict):
        result = {}
        filters = [
            {"Name": "name", "Values": [self.ami_name_pattern]},
            {"Name": "state", "Values": ["available"]},
        ]
        for k, v in filter(
            lambda k: k[0] not in ["name", "state"],
            source_ami_filter.get("filters", {}).items(),
        ):
            filters.append({"Name": k, "Values": v if isinstance(v, list) else [v]})
        result["Filters"] = filters

        owners = source_ami_filter.get("owners")
        if owners:
            result["Owners"] = owners

        return result

    def load(self):
        self.dirty = False
        with open(self.filename, "r") as f:
            self.packer = json.load(f)

    def save(self):
        if self.dry_run:
            return
        if self.dirty:
            with open(self.filename, "w") as f:
                self.packer = json.dump(self.packer, f, indent=2)

    def update(self):
        builders = filter(
            lambda b: b["type"]
            in [
                "amazon-chroot",
                "amazon-ebs",
                "amazon-ebssurrogate",
                "amazon-instance",
            ],
            self.packer.get("builders", []),
        )
        for builder in builders:
            source_ami_filter = builder.get("source_ami_filter", {})
            if self.is_source_filter_name_match(source_ami_filter):
                old_name = source_ami_filter.get("filters", {}).get("name")
                request = self.create_describe_image_request(source_ami_filter)
                images = sorted(
                    self.ec2.describe_images(**request)["Images"],
                    key=lambda c: c["CreationDate"],
                )
                if images:
                    name = images[-1]["Name"]
                    if name != old_name:
                        source_ami_filter["filters"]["name"] = name
                        self.dirty = True
                        sys.stderr.write(
                            f"INFO: replacing source ami filter image name with {name} of builder {builder['type']}"
                        )
                    else:
                        sys.stderr.write(
                            f"INFO: source ami filter already up to date with image name {name} of builder {builder['type']}"
                        )


@click.command(name="packer-latest-ami", help=PackerAMIUpdater.__doc__)
@click.option(
    "--ami-name-pattern",
    required=True,
    help="glob style pattern of the AMI image name to use",
)
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def main(ctx, ami_name_pattern, path):
    updater = PackerAMIUpdater()
    updater.dry_run = ctx.obj.get("dry_run") if ctx.obj else False
    updater.verbose = ctx.obj.get("verbose") if ctx.obj else False
    updater.ami_name_pattern = ami_name_pattern
    for filename in path:
        updater.filename = filename
        updater.load()
        updater.update()
        updater.save()


if __name__ == "__main__":
    main()
