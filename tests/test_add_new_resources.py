import pathlib
import tempfile

from ruamel.yaml import YAML

from aws_cfn_update.add_missing_resources import add_missing_resources
from aws_cfn_update.cfn_updater import read_template


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


def test_read_template():
    source = {
        "Resources": {"AMI": {}, "EC2Instance": {"ImageId": {"Ref": "AMI"}}},
        "Outputs": {"XXX": {"Value": "bla"}},
    }
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        YAML(typ="safe").dump(source, pathlib.Path(f.name))
        result = read_template(f.name)
        assert source == result
