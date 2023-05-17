from aws_cfn_update.replace_references import replace_references
from aws_cfn_update.cfn_updater import CfnUpdater
from io import StringIO


def test_simple():
    template = {"Ref": "Old"}
    assert replace_references(template, "Old", "New")
    assert template["Ref"] == "New"

    template = {"DependsOn": [{"Ref": "Old"}]}
    assert replace_references(template, "Old", "New")
    assert template["DependsOn"][0]["Ref"] == "New"

    template = "Old"
    assert not replace_references(template, "Old", "New")
    assert template == "Old"

    template = {"DependsOn": [{"Ref": "Old"}]}
    assert not replace_references(template, "Oud", "New")
    assert template["DependsOn"][0]["Ref"] == "Old"


def test_yaml():
    yaml = CfnUpdater().yaml
    template = yaml.load("---\nAMI: !Ref Old")
    assert replace_references(template, "Old", "New")

    result = StringIO()
    yaml.dump(template, result)
    assert result.getvalue() == "---\nAMI: !Ref New\n"
