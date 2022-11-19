"""
update_packer unit test.
"""
import boto3
import unittest
from tests.update_packer.base import UpdatePackerUnitTestBase
from aws_cfn_update.packer_ami_updater import PackerAMIUpdater


class UpdatePackerUnitTest(UpdatePackerUnitTestBase):
    def test_update_packer(self) -> None:
        packer = {
            "builders": [
                {
                    "type": "amazon-ebs",
                    "communicator": "winrm",
                    "region": "eu-central-1",
                    "source_ami_filter": {
                        "filters": {
                            "virtualization-type": "hvm",
                            "name": "Windows_Server-2016-English-Full-Base-2020.01.10",
                            "root-device-type": "ebs",
                        },
                        "owners": ["801119661308"],
                    },
                }
            ]
        }
        old_name = packer["builders"][0]["source_ami_filter"]["filters"]["name"]
        boto3.DEFAULT_SESSION = self.session
        updater = PackerAMIUpdater()
        updater.ami_name_pattern = "Windows_Server-2016-English-Full-Base*"
        updater.packer = packer
        updater.update()
        assert updater.dirty
        new_name = packer["builders"][0]["source_ami_filter"]["filters"]["name"]
        assert old_name != new_name

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()


if __name__ == "__main__":
    unittest.main()
