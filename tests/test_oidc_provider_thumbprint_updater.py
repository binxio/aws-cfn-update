import pytest
from aws_cfn_update.oidc_provider_thumbprints_updater import (
    OIDCProviderThumbprintsUpdater,
)
import json


_single_oidc_provider = {
    "Resources": {
        "GitLabCom": {
            "Type": "AWS::IAM::OIDCProvider",
            "Properties": {
                "Url": "https://gitlab.com",
                "ThumbprintList": ["DEADBEEF"],
                "ClientIdList": ["https://gitlab.com"],
            },
        }
    }
}

_multiple_oidc_providers = {
    "Resources": {
        "GitLabCom": {
            "Type": "AWS::IAM::OIDCProvider",
            "Properties": {
                "Url": "https://gitlab.com",
                "ThumbprintList": ["DEADBEEF"],
                "ClientIdList": ["https://gitlab.com"],
            },
        },
        "GoogleCom": {
            "Type": "AWS::IAM::OIDCProvider",
            "Properties": {"Url": "https://accounts.google.com"},
        },
    }
}


@pytest.mark.parametrize("verbose_mode", [True, False])
def test_replace(verbose_mode):
    updater = OIDCProviderThumbprintsUpdater()
    updater.template = json.loads(json.dumps(_single_oidc_provider))

    updater.update_template()
    assert updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 1
    fingerprint = thumbprints[0]
    assert fingerprint != "DEADBEEF"

    updater.dirty = False
    updater.update_template()
    assert not updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 1
    assert fingerprint == thumbprints[0]


@pytest.mark.parametrize("verbose_mode", [True, False])
def test_append(verbose_mode):
    updater = OIDCProviderThumbprintsUpdater()
    updater.template = json.loads(json.dumps(_single_oidc_provider))
    updater.append = True

    updater.update_template()
    assert updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 2
    fingerprint = thumbprints[-1]
    assert fingerprint != "DEADBEEF"

    updater.dirty = False
    updater.update_template()
    assert not updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 2
    assert fingerprint == thumbprints[-1]


@pytest.mark.parametrize("verbose_mode", [True, False])
def test_single(verbose_mode):
    updater = OIDCProviderThumbprintsUpdater()
    updater.template = json.loads(json.dumps(_single_oidc_provider))
    updater.url = "https://accounts.google.com"

    updater.update_template()
    assert not updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 1
    fingerprint = thumbprints[0]
    assert fingerprint == "DEADBEEF"

    updater.url = "https://gitlab.com"
    updater.update_template()
    assert updater.dirty

    thumbprints = updater.template["Resources"]["GitLabCom"]["Properties"][
        "ThumbprintList"
    ]
    assert len(thumbprints) == 1
    fingerprint = thumbprints[0]
    assert fingerprint != "DEADBEEF"


@pytest.mark.parametrize("verbose_mode", [True, False])
def test_update_all(verbose_mode):
    updater = OIDCProviderThumbprintsUpdater()
    updater.template = json.loads(json.dumps(_multiple_oidc_providers))

    updater.update_template()
    assert updater.dirty
