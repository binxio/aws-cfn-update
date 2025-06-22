import boto3
import botocore

from aws_cfn_update.packer_ami_updater import PackerAMIUpdater
from unittest import TestCase


class TestAMIUpdater(TestCase):
    def setUp(self):
        self.session = botocore.session.get_session(
            {"region": ("region", "AWS_DEFAULT_REGION", "eu-central-1", None)}
        )
        self.session.set_credentials(self, "deadbeef", "deadbeef")
        boto3.setup_default_session(botocore_session=self.session)
        assert boto3.DEFAULT_SESSION

    def tearDown(self) -> None:
        boto3.DEFAULT_SESSION = None

    def test_is_source_filter_name_match(self):
        updater = PackerAMIUpdater()

        source_ami_filter = {"filters": {"name": "Windows_Server 2016 2020.02.10"}}
        updater.ami_name_pattern = "Windows_Server 2016*"
        assert updater.is_source_filter_name_match(source_ami_filter)

        source_ami_filter = {"filters": {"blabla": "Windows_Server 2016 2020.02.10"}}
        assert not updater.is_source_filter_name_match(source_ami_filter)
        assert not updater.is_source_filter_name_match({})

    def test_create_describe_image_request(self):
        source_ami_filter = {
            "filters": {
                "virtualization-type": "hvm",
                "name": "Windows_Server-2016-English-Full-Base-2020.01.10",
                "root-device-type": "ebs",
            },
            "owners": ["801119661308"],
        }
        updater = PackerAMIUpdater()
        updater.ami_name_pattern = "Windows_Server-2016-English-Full-Base-*"
        response = updater.create_describe_image_request(source_ami_filter)
        assert response["Owners"] == source_ami_filter["owners"]
        assert has_filter(response["Filters"], "virtualization-type", ["hvm"])
        assert has_filter(response["Filters"], "name", [updater.ami_name_pattern])
        assert has_filter(response["Filters"], "state", ["available"])
        assert has_filter(response["Filters"], "root-device-type", ["ebs"])

        source_ami_filter = {
            "filters": {
                "virtualization-type": "hvm",
                "name": "Windows_Server-2016-English-Full-Base-2020.01.10",
                "root-device-type": "ebs",
            }
        }
        response = updater.create_describe_image_request(source_ami_filter)
        assert not response.get("Owners")


def has_filter(filters, name, values):
    return next(
        filter(lambda f: f["Name"] == name and f["Values"] == values, filters), None
    )
