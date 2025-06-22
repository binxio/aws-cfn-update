"""
Generated base class for the update_packer unit test. The setup will provide stubbed
responses for all recorded requests.

** generated code - do not edit **
"""
import unittest
import botocore.session
from botocore.stub import Stubber

from tests.update_packer import call_00001_describe_images


class UpdatePackerUnitTestBase(unittest.TestCase):
    def setUp(self) -> None:
        """
        add stubs for all AWS API calls
        """
        self.session = botocore.session.get_session(
            {"region": ("region", "AWS_DEFAULT_REGION", "eu-central-1", None)}
        )
        self.clients = {
            service: self.session.create_client(service) for service in ["ec2"]
        }
        self.stubs = {
            service: Stubber(client) for service, client in self.clients.items()
        }

        self.stubs["ec2"].add_response(
            "describe_images",
            call_00001_describe_images.response,
            call_00001_describe_images.request,
        )

        for _, stub in self.stubs.items():
            stub.activate()
        self.session.client = lambda x: self.clients[x]

    def tearDown(self) -> None:
        """
        check all api calls were executed
        """
        for service, stub in self.stubs.items():
            stub.assert_no_pending_responses()
            stub.deactivate()
