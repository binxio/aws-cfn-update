import os
import json
from aws_cfn_update.latest_ami_updater import AMIUpdater, make_new_resource_name


def test_new_resource_name():
    updater = stubbed_ami_updater()
    result = make_new_resource_name("WhatEverBaseAMI")
    assert result == "WhatEverBaseAMIv1"

    result = make_new_resource_name(result)
    assert result == "WhatEverBaseAMIv2"

    result = make_new_resource_name("WhatEv1rBaseAMIv3")
    assert result == "WhatEv1rBaseAMIv4"


def test_ami_update_inplace():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.a-amazon-ecs-optimized"}
                },
            }
        }
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.update_template()
    assert updater.dirty
    assert template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )


def test_with_other_filters():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {
                        "name": "amzn-ami-2013.09.a-amazon-ecs-optimized",
                        "owner-alias": "amazon",
                        "is-public": "true",
                    },
                    "Owners": ["amazon"],
                },
            }
        }
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.update_template()
    assert updater.dirty
    assert template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )


def test_no_matching_ami_found():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {
                        "name": "amzn-ami-2013.09.a-amazon-ecs-optimized",
                        "owner-alias": "amazon",
                        "is-public": "false",
                    },
                    "Owners": ["microsoft"],
                },
            }
        }
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.update_template()
    assert not updater.dirty
    assert template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )


def test_add_new_version():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.a-amazon-ecs-optimized"}
                },
            }
        },
        "Outputs": {"AMI": {"Ref": "CustomAMI"}},
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.add_new_version = True
    updater.update_template()
    assert updater.dirty
    assert "CustomAMIv1" in template["Resources"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomAMIv1"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert template["Outputs"]["AMI"]["Ref"] == "CustomAMIv1"


def test_add_new_version_partitions():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.a-amazon-ecs-optimized"}
                },
            },
            "CustomBMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2016.09.a-amazon-ecs-optimized"}
                },
            },
        },
        "Outputs": {"AMI": {"Ref": "CustomAMI"}, "BMI": {"Ref": "CustomBMI"}},
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.add_new_version = True
    updater.update_template()
    assert updater.dirty
    assert "CustomAMIv1" in template["Resources"]
    assert "CustomBMIv1" in template["Resources"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomBMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2016.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomAMIv1"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomBMIv1"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2016.09.a-amazon-ecs-optimized"
    )
    assert template["Outputs"]["AMI"]["Ref"] == "CustomAMIv1"
    assert template["Outputs"]["BMI"]["Ref"] == "CustomBMIv1"


def test_add_new_version_partitions_multiple_versions():
    template = {
        "Resources": {
            "CustomAMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.a-amazon-ecs-optimized"}
                },
            },
            "CustomAMIv2": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.b-amazon-ecs-optimized"}
                },
            },
            "CustomBMI": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2016.09.a-amazon-ecs-optimized"}
                },
            },
        },
        "Outputs": {"AMI": {"Ref": "CustomAMI"}, "BMI": {"Ref": "CustomBMI"}},
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.add_new_version = True
    updater.update_template()
    assert updater.dirty
    assert "CustomAMIv3" in template["Resources"]
    assert "CustomBMIv1" in template["Resources"]
    assert (
        template["Resources"]["CustomAMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomBMI"]["Properties"]["Filters"]["name"]
        == "amzn-ami-2016.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomAMIv3"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2013.09.a-amazon-ecs-optimized"
    )
    assert (
        template["Resources"]["CustomBMIv1"]["Properties"]["Filters"]["name"]
        > "amzn-ami-2016.09.a-amazon-ecs-optimized"
    )
    assert template["Outputs"]["AMI"]["Ref"] == "CustomAMIv3"
    assert template["Outputs"]["BMI"]["Ref"] == "CustomBMIv1"


def test_add_new_versions_keep_old_refs():
    template = {
        "Resources": {
            "CustomAMIv2": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.b-amazon-ecs-optimized"}
                },
            },
            "CustomAMIv1": {
                "Type": "Custom::AMI",
                "Properties": {
                    "Filters": {"name": "amzn-ami-2013.09.a-amazon-ecs-optimized"}
                },
            },
        },
        "Outputs": {"OldAMI": {"Ref": "CustomAMIv1"}, "NewAMI": {"Ref": "CustomAMIv2"}},
    }
    updater = stubbed_ami_updater()
    updater.template = template
    updater.ami_name_pattern = "amzn-ami-*ecs-optimized"
    updater.add_new_version = True
    updater.update_template()
    assert updater.dirty
    assert "CustomAMIv3" in template["Resources"]
    assert template["Outputs"]["OldAMI"]["Ref"] == "CustomAMIv1"
    assert template["Outputs"]["NewAMI"]["Ref"] == "CustomAMIv3"


all_responses = []
with open(os.path.join(os.path.dirname(__file__), "dummy_responses.json"), "r") as f:
    all_dummy_responses = json.load(f)


def stubbed_ami_updater():
    result = AMIUpdater()
    result._describe_images = describe_images_stub
    return result


def describe_images_stub(**request):
    result = next(
        filter(lambda rr: rr["request"] == request, all_dummy_responses), None
    )
    if not result:
        assert False, "no dummy response found for this request"
    return result["response"]
