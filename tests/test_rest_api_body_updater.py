import json
import os

from aws_cfn_update.rest_api_body_updater import RestAPIBodyUpdater


def test_new_resource_name():
    updater = RestAPIBodyUpdater()

    updater.resource_name = "RestAPI"
    result = updater.new_resource_name("RestAPI")
    assert result == "RestAPIv1"

    result = updater.new_resource_name(result)
    assert result == "RestAPIv2"

    updater.resource_name = "Restv2Api"
    result = updater.new_resource_name("Restv2Apiv3")
    assert result == "Restv2Apiv4"


def test_matching_names():
    updater = RestAPIBodyUpdater()
    updater.resource_name = "RestAPI"
    updater.template = {
        "Resources": {
            "RestAPIv10": {"Type": "AWS::ApiGateway::RestApi"},
            "RestApi": {"Type": "AWS::ApiGateway::RestApi"},
            "Restv2APiv1": {"Type": "AWS::ApiGateway::RestApi"},
            "RestAPIv1": {"Type": "AWS::ApiGateway::RestApi"},
            "RestAPIv0": {"Type": "AWS::ApiGateway::RestApi"},
            "RestAPIv_01": {"Type": "AWS::ApiGateway::RestApi"},
        }
    }

    result = updater.find_matching_resources()
    assert result == ["RestAPIv0", "RestAPIv1", "RestAPIv10"]

    updater.resource_name = "RestApi"
    result = updater.find_matching_resources()
    assert result == ["RestApi"]

    updater.resource_name = "NotARestApi"
    result = updater.find_matching_resources()
    assert not result


sample = {
    "Resources": {
        "Deployment": {
            "Type": "AWS::ApiGateway::Deployment",
            "Properties": {"RestApiId": {"Ref": "RestAPI"}},
        },
        "RestAPI": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "EndpointConfiguration": {"Types": ["REGIONAL"]},
                "Body": {"swagger": "2.0"},
            },
        },
    }
}


def test_replace_body():
    updater = RestAPIBodyUpdater()
    updater.resource_name = "RestAPI"
    updater.template = json.loads(json.dumps(sample))
    updater.body = {"swagger": "2.0", "description": "a new one"}

    updater.update_template()
    assert updater.dirty
    assert (
        "description" in updater.template["Resources"]["RestAPI"]["Properties"]["Body"]
    )
    assert (
        updater.template["Resources"]["RestAPI"]["Properties"]["Body"]["description"]
        == "a new one"
    )


def test_add_new_version():
    updater = RestAPIBodyUpdater()
    updater.resource_name = "RestAPI"
    updater.template = json.loads(json.dumps(sample))
    updater.body = {"swagger": "2.0", "description": "a new one"}

    updater.add_new_version = True
    updater.update_template()
    assert updater.dirty
    assert "RestAPI" not in updater.template["Resources"]
    assert "RestAPIv1" in updater.template["Resources"]
    assert (
        "description"
        in updater.template["Resources"]["RestAPIv1"]["Properties"]["Body"]
    )
    assert (
        updater.template["Resources"]["RestAPIv1"]["Properties"]["Body"]["description"]
        == "a new one"
    )


multiple = {
    "Resources": {
        "Deployment": {
            "Type": "AWS::ApiGateway::Deployment",
            "Properties": {"RestApiId": {"Ref": "RestAPIv3"}},
        },
        "RestAPI": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "EndpointConfiguration": {"Types": ["REGIONAL"]},
                "Body": {"swagger": "2.0"},
            },
        },
        "RestAPIv2": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "EndpointConfiguration": {"Types": ["REGIONAL"]},
                "Body": {"swagger": "2.0"},
            },
        },
        "RestAPIv3": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "EndpointConfiguration": {"Types": ["GLOBAL"]},
                "Body": {"swagger": "2.0"},
            },
        },
    }
}


def test_add_new_version_keep_two():
    updater = RestAPIBodyUpdater()
    updater.resource_name = "RestAPI"
    updater.template = json.loads(json.dumps(multiple))
    updater.body = {"swagger": "2.0", "description": "a new one"}

    updater.add_new_version = True
    updater.keep = 2
    updater.update_template()
    assert updater.dirty
    assert "RestAPI" not in updater.template["Resources"]
    assert "RestAPIv2" not in updater.template["Resources"]
    assert "RestAPIv3" in updater.template["Resources"]
    assert "RestAPIv4" in updater.template["Resources"]
    assert (
        "GLOBAL"
        == updater.template["Resources"]["RestAPIv4"]["Properties"][
            "EndpointConfiguration"
        ]["Types"][0]
    )
    assert (
        "description"
        in updater.template["Resources"]["RestAPIv4"]["Properties"]["Body"]
    )
    assert (
        updater.template["Resources"]["RestAPIv4"]["Properties"]["Body"]["description"]
        == "a new one"
    )

    assert (
        updater.template["Resources"]["Deployment"]["Properties"]["RestApiId"]["Ref"]
        == "RestAPIv4"
    )


def test_load_and_merge():
    test_directory = os.path.dirname(os.path.abspath(__file__))
    updater = RestAPIBodyUpdater()
    updater.resource_name = "RestAPI"
    updater.template = json.loads(json.dumps(sample))
    updater.api_gateway_extensions = f"{test_directory}/aws-extensions.yaml"
    updater.open_api_specification = f"{test_directory}/api-specification.yaml"
    updater.body = updater.load_and_merge_swagger_body()
    updater.update_template()

    assert updater.dirty
    assert (
        updater.template["Resources"]["RestAPI"]["Properties"]["Body"] == updater.body
    )
