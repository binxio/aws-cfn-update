from aws_cfn_update.config_rule_inline_code_updater import (
    ConfigRuleInlineCodeUpdater as Updater,
)
import json


sample = {
    "Resources": {
        "ConfigRule": {
            "Type": "AWS::Config::ConfigRule",
            "Properties": {
                "Source": {
                    "Owner": "CUSTOM_POLICY",
                    "CustomPolicyDetails": {
                        "EnableDebugLogDelivery": "true",
                        "PolicyRuntime": "guard-2.x.x",
                    },
                }
            },
        }
    }
}


def test_add_body():
    updater = Updater()
    updater.resource_name = "ConfigRule"
    updater.code = 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'
    updater.template = sample.copy()

    updater.update_template()
    assert updater.dirty
    assert "Properties" in updater.template["Resources"]["ConfigRule"]

    assert "Source" in updater.template["Resources"]["ConfigRule"]["Properties"]
    source = updater.template["Resources"]["ConfigRule"]["Properties"]["Source"]
    assert "CustomPolicyDetails" in source

    assert "CUSTOM_POLICY" == source["Owner"]
    assert "true" == source["CustomPolicyDetails"]["EnableDebugLogDelivery"]
    assert "guard-2.x.x" in source["CustomPolicyDetails"]["PolicyRuntime"]

    assert (
        source["CustomPolicyDetails"]["PolicyText"]
        == 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'
    )


def test_replace_body():
    updater = Updater()
    updater.resource_name = "ConfigRule"
    updater.code = 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'
    updater.template = sample.copy()
    updater.template["Resources"]["ConfigRule"]["Properties"]["Source"][
        "CustomPolicyDetails"
    ]["PolicyText"] = "Existing Policy"

    updater.update_template()
    assert updater.dirty
    assert "Properties" in updater.template["Resources"]["ConfigRule"]

    assert "Source" in updater.template["Resources"]["ConfigRule"]["Properties"]
    source = updater.template["Resources"]["ConfigRule"]["Properties"]["Source"]
    assert "CustomPolicyDetails" in source

    assert "CUSTOM_POLICY" == source["Owner"]
    assert "true" == source["CustomPolicyDetails"]["EnableDebugLogDelivery"]
    assert "guard-2.x.x" in source["CustomPolicyDetails"]["PolicyRuntime"]

    assert (
        source["CustomPolicyDetails"]["PolicyText"]
        == 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'
    )


skip_body_sample = {"Resources": {"ConfigRule": {"Type": "AWS::EC2::Instance"}}}


def test_skip_body():
    updater = Updater()
    updater.resource_name = "ConfigRule"
    updater.code = 'print("hello world!")'
    updater.template = skip_body_sample.copy()

    updater.update_template()
    assert not updater.dirty
    assert "Properties" not in updater.template["Resources"]["ConfigRule"]
