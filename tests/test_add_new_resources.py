from aws_cfn_update.rest_api_body_updater import RestAPIBodyUpdater
import json

from aws_cfn_update.add_missing_resources import add_missing_resources
from aws_cfn_update.cfn_updater import yaml


def test_simple():
    source = {"Resources": {"AMI": {}, "EC2Instance": {"ImageId": {"Ref": "AMI"}}}}
    target = {"Resources": {"AMI": {}}}
    result = add_missing_resources(target, source)
    assert result
    assert target == source


def test_add_all():
    source = {
        "Parameters": {"VPC": {"Type": "String"}},
        "Resources": {"AMI": {}, "EC2Instance": {"ImageId": {"Ref": "AMI"}}},
        "Conditions": {"IsTrue": {"Fn::Equals": ["true", "false"]}},
        "Mappings": {"XXX": {"Type": "String"}},
    }
    target = {"Resources": {"AMI": {}}}
    result = add_missing_resources(target, source)
    assert result
    assert target == source


def test_add_no_outputs():
    source = {
        "Resources": {"AMI": {}, "EC2Instance": {"ImageId": {"Ref": "AMI"}}},
        "Outputs": {"XXX": {"Value": "bla"}},
    }
    target = {"Resources": {"AMI": {}}}
    result = add_missing_resources(target, source)
    assert target["Resources"].get("EC2Instance")
    assert not target.get("Outputs")
