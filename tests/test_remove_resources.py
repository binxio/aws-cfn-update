from aws_cfn_update.remove_resource import remove_resource_from_template
from aws_cfn_update.cfn_updater import CfnUpdater
from io import StringIO
from ruamel.yaml import YAML


def test_simple():
    template = {"Resources": {"AMI": {}}}
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None


def test_simple_ref():
    template = {"Resources": {"AMI": {}, "EC2Instance": {"ImageId": {"Ref": "AMI"}}}}
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("ECInstance") is None


def test_get_att():
    template = {"Resources": {"AMI": {}, "EC2Instance": {"FN::GetAtt": ["AMI", "Arn"]}}}
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_nested_ref():
    template = {
        "Resources": {"AMI": {}, "EC2Instance": {"FN::GetAtt": [{"Ref": "AMI"}, "Arn"]}}
    }
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_array_reference():
    template = {
        "Resources": {
            "AMI": {},
            "EC2Instance": {"ImageIds": [{"Ref": "AMI"}, {"Ref": "None"}]},
        }
    }
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("AMI") is None


def test_yaml():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: !Ref Old
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None


def test_yaml_simple_ref():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Ref AMI
Outputs:
  Arn:    
     Value: !GetAtt AMI.Arn
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    resources = template.get("Resources")
    assert resources.get("AMI") is None
    assert resources.get("EC2Instance") is None
    outputs = template.get("Outputs")
    assert outputs.get("Arn") is None


def test_yaml_simple_getatt():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !GetAtt
      - AMI
      - Arn
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_yaml_nested_ref():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !GetAtt
      - !Ref AMI
      - Arn
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_yaml_ref_in_sub():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Sub '${AMI}'
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_yaml_no_ref_in_sub():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Sub '${!AMI}'
"""
    )

    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance")


def test_yaml_ref_in_sub_array_style():
    yaml = CfnUpdater().yaml
    template = yaml.load(
        """
Resources:
  AMI: 
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Sub
      - '${AmiReference}'
      - AmiReference: !Ref AMI
"""
    )
    assert template.get("Resources", {}).get("AMI")
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_json_sub():
    template = {"Resources": {"AMI": {}, "EC2Instance": {"FN::Sub": "${AMI}"}}}
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None


def test_json_sub():
    template = {
        "Resources": {
            "AMI": {},
            "EC2Instance": {"FN::Sub": ["${AmiRef}", {"AmiRef": {"Ref": "AMI"}}]},
        }
    }
    remove_resource_from_template(template, "AMI")
    assert template.get("Resources", {}).get("AMI") is None
    assert template.get("Resources", {}).get("EC2Instance") is None
