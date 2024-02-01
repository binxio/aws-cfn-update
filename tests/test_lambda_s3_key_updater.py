from aws_cfn_update.lambda_s3_key_updater import LambdaS3KeyUpdater as Updater
from copy import deepcopy


sample = {
    "Resources": {
        "0": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Code": {
                    "S3Bucket": "test-bucket",
                    "S3Key": "lambdas/cfn-listener-rule-provider-0.1.0.zip",
                },
            },
        },
        "1": {
            "Type": "AWS::Lambda::Function",
            "Properties": {
                "Code": {
                    "S3Bucket": "test-bucket",
                    "S3Key": "lambdas/iam-sudo-0.0.0.zip",
                },
            },
        },
    }
}


def test_simple_keys():
    updater = Updater()
    updater.s3_keys = [
        "lambdas/cfn-listener-rule-provider-1.0.0.zip",
    ]
    updater.template = deepcopy(sample)

    assert (
        updater.template["Resources"]["1"]["Properties"]["Code"]["S3Key"]
        == sample["Resources"]["1"]["Properties"]["Code"]["S3Key"]
    )
    updater.update_template()
    assert updater.dirty
    for i, s3_key in enumerate(updater.s3_keys):
        new_value = updater.template["Resources"][f"{i}"]["Properties"]["Code"]["S3Key"]
        assert s3_key == new_value


def test_multiple_keys():
    updater = Updater()
    updater.s3_keys = [
        "lambdas/cfn-listener-rule-provider-1.0.0.zip",
        "lambdas/iam-sudo-1.0.0.zip",
    ]
    updater.template = deepcopy(sample)

    updater.update_template()
    assert updater.dirty
    for i, s3_key in enumerate(updater.s3_keys):
        new_value = updater.template["Resources"][f"{i}"]["Properties"]["Code"]["S3Key"]
        assert s3_key == new_value


def test_non_semver_s3_key():
    updater = Updater()
    try:
        updater.s3_keys = [
            "lambdas/cfn-listener-rule-provider.zip",
        ]
        assert False, "expected invalid semver version error"
    except ValueError as error:
        assert error.args == (
            "lambdas/cfn-listener-rule-provider.zip is not a semver S3Key",
        )
        pass


def test_no_updates():
    updater = Updater()
    updater.s3_keys = [
        "lambdas/cfn-secret-provider-1.0.0.zip",
    ]
    updater.template = deepcopy(sample)
    updater.update_template()
    assert not updater.dirty
