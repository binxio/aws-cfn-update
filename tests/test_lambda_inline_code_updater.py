from aws_cfn_update.lambda_inline_code_updater import LambdaInlineCodeUpdater as Updater
import json


sample = {"Resources": {"Lambda": {"Type": "AWS::Lambda::Function"}}}


def test_replace_body():
    updater = Updater()
    updater.resource = "Lambda"
    updater.code = 'print("hello world!")'
    updater.template = sample.copy()

    updater.update_template()
    assert updater.dirty
    assert "Properties" in updater.template["Resources"]["Lambda"]
    assert "Code" in updater.template["Resources"]["Lambda"]["Properties"]
    assert "ZipFile" in updater.template["Resources"]["Lambda"]["Properties"]["Code"]
    assert (
        updater.template["Resources"]["Lambda"]["Properties"]["Code"]["ZipFile"]
        == 'print("hello world!")'
    )


skip_body_sample = {"Resources": {"Lambda": {"Type": "AWS::EC2::Instance"}}}


def test_skip_body():
    updater = Updater()
    updater.resource = "Lambda"
    updater.code = 'print("hello world!")'
    updater.template = skip_body_sample.copy()

    updater.update_template()
    assert not updater.dirty
    assert "Properties" not in updater.template["Resources"]["Lambda"]
