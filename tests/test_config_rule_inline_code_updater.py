from aws_cfn_update.config_rule_inline_code_updater import ConfigRuleInlineCodeUpdater as Updater
import json


sample = {
    "Resources": {
        "ConfigRule": {
            "Type": "AWS::Config::ConfigRule"
        }
    }
}


def test_replace_body():
    updater = Updater()
    updater.resource = 'ConfigRule'
    updater.code = 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'
    updater.template = sample.copy()

    updater.update_template()
    assert updater.dirty
    assert 'Properties' in updater.template['Resources']['ConfigRule']

    assert 'Source' in updater.template['Resources']['ConfigRule']['Properties']
    assert 'CustomPolicyDetails' in updater.template['Resources']['ConfigRule']['Properties']['Source']
    assert 'PolicyText' in updater.template['Resources']['ConfigRule']['Properties']['Source']['CustomPolicyDetails']


    assert updater.template['Resources']['ConfigRule']['Properties']['Source']['CustomPolicyDetails']['PolicyText'] == 'let buckets = Resources.*[ Type == "AWS::S3::Bucket" ]'


skip_body_sample = {
    "Resources": {
        "ConfigRule": {
            "Type": "AWS::EC2::Instance"
        }
    }
}


def test_skip_body():
    updater = Updater()
    updater.resource = 'ConfigRule'
    updater.code = 'print("hello world!")'
    updater.template = skip_body_sample .copy()

    updater.update_template()
    assert not updater.dirty
    assert 'Properties' not in updater.template['Resources']['ConfigRule']
