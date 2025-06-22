import textwrap

from aws_cfn_update.container_image_updater import ContainerImageUpdater as Updater
from copy import deepcopy


sample = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Resources": {
        "AMI": {
            "Type": "Custom::AMI",
            "Properties": {
                "Filters": {"name": "amzn-ami-2017.09.a-amazon-ecs-optimized"}
            },
        },
        "TaskDefinition": {
            "Type": "AWS::ECS::TaskDefinition",
            "Properties": {
                "Family": "testme",
                "NetworkMode": "bridge",
                "ContainerDefinitions": [
                    {
                        "Name": "paas-monitor",
                        "Image": "mvanholsteijn/paas-monitor:latest",
                    },
                    {"Name": "sidecar", "Image": "cloud_sql_proxy:latest"},
                ],
            },
        },
    },
}


def test_single_update():
    new_images = ["mvanholsteijn/paas-monitor:0.6.0"]
    updater = Updater()
    updater.filename = "test.json"
    updater.images = new_images
    updater.template = deepcopy(sample)

    updater.update_template()
    assert updater.dirty
    for image in new_images:
        new_value = updater.template["Resources"]["TaskDefinition"]["Properties"][
            "ContainerDefinitions"
        ][0]["Image"]
        assert image == new_value


def test_multiple_update():
    new_images = ["mvanholsteijn/paas-monitor:0.6.0", "cloud_sql_proxy:3.3.0"]
    updater = Updater()
    updater.filename = "test.json"
    updater.images = new_images
    updater.template = deepcopy(sample)

    updater.update_template()
    assert updater.dirty
    for i, image in enumerate(new_images):
        new_value = updater.template["Resources"]["TaskDefinition"]["Properties"][
            "ContainerDefinitions"
        ][i]["Image"]
        assert image == new_value


def test_no_updates():
    updater = Updater()
    updater.images = [
        "lambdas/cfn-secret-provider:1.0.0",
    ]
    updater.template = deepcopy(sample)
    updater.update_template()
    assert not updater.dirty


def test_invalid_container_image():
    updater = Updater()
    try:
        updater.images = [
            "alpine",
        ]
    except ValueError as error:
        assert error.args == ("alpine is an invalid image name",)


def test_container_image_reference_not_found():
    template = textwrap.dedent(
        """
        AWSTemplateFormatVersion: '2010-09-09'
        Parameters:
          PaasMonitorImage: String
        
        Resources:
          AMI:
            Type: Custom::AMI
            Properties:
              Filters:
                name: amzn-ami-2017.09.a-amazon-ecs-optimized
          TaskDefinition:
            Type: AWS::ECS::TaskDefinition
            Properties:
              Family: testme
              NetworkMode: bridge
              ContainerDefinitions:
                - Name: paas-monitor
                  Image: !Ref PaasMonitorImage

    """
    )
    new_images = ["mvanholsteijn/paas-monitor:0.6.0"]

    updater = Updater()
    updater.filename = "test.yaml"
    updater.images = new_images
    updater.template = updater.yaml.load(template)

    updater.update_template()
    assert not updater.dirty
