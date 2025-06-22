#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Copyright 2018 binx.io B.V.
import binascii
import ssl
import sys
from urllib.parse import urlparse

import click
import requests
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from ruamel.yaml import CommentedSeq
from aws_cfn_update.cfn_updater import CfnUpdater


class OIDCProviderThumbprintsUpdater(CfnUpdater):
    """
    Updates the thumbprints list of an AWS::IAM::OIDCProvider.

    By default, it updates the thumbprints of all OIDCProviders specified
    templates.
    """

    def __init__(self):
        super(OIDCProviderThumbprintsUpdater, self).__init__()
        self.url = None
        self.verbose = False
        self.dry_run = False
        self.append = False

    def new_value(self, definition):
        if self.with_fn_sub:
            return isinstance(definition, dict) and definition.get(
                "Fn::Sub"
            ) == self.definition, {"Fn::Sub": self.definition}
        else:
            return definition == self.definition, self.definition

    def update_template(self):
        """
        updates the Thumbprints of OIDCProviders
        """
        resources: dict = self.template.get("Resources", {})
        for name in self.all_matching_oidc_providers(resources):
            provider = resources[name]
            self.update_thumbprints(name, provider)

    @staticmethod
    def is_type_oidc_provider(resource):
        """
        returns true if the resource is of type AWS::IAM::OIDCProvider
        """
        return resource.get("Type", "") == "AWS::IAM::OIDCProvider"

    def is_matching_oidc_provider(self, provider):
        """
        Returns true if there is a match on self.url and the url starts with https://.
        """
        url = provider.get("Properties", {}).get("Url")
        if not (url and url.startswith("https://")):
            return False

        if not self.url:
            return True

        return url == self.url

    def all_matching_oidc_providers(self, resources):
        return filter(lambda n: self.is_matching_oidc_provider(resources[n]), resources)

    def main(self, url, append, path, dry_run, verbose):
        self.dry_run = dry_run
        self.verbose = verbose
        self.url = url
        self.append = append
        self.update(path)

    @staticmethod
    def get_public_key(url: str):
        wks = f"{url}/.well-known/openid-configuration"
        response = requests.get(wks, headers={"Accept": "application/json"})
        if response.status_code != 200:
            raise ValueError(
                "expected 200 from %s, got %d, %s",
                url,
                response.status_code,
                response.text,
            )

        configuration = response.json()
        if "jwks_uri" not in configuration:
            raise ValueError("%s did not return a proper openid configuration", wks)

        jwks_uri = urlparse(configuration["jwks_uri"])

        conn = None
        try:
            conn = ssl.create_connection((jwks_uri.netloc, 443))
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            sock = context.wrap_socket(conn, server_hostname=jwks_uri.netloc)
            certificate = ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))
            return x509.load_pem_x509_certificate(
                certificate.encode("ascii"), default_backend()
            )
        finally:
            if conn:
                conn.close()

    def update_thumbprints(self, name, provider):
        url = provider.get("Properties", {}).get("Url")
        public_key = self.get_public_key(url)
        sha1 = public_key.fingerprint(hashes.SHA1())
        fingerprint = binascii.hexlify(sha1).decode("ascii").lower()

        thumbprints = provider.get("Properties", {}).get(
            "ThumbprintList", CommentedSeq()
        )
        exists = list(filter(lambda f: f.lower() == fingerprint, thumbprints))
        if exists:
            if self.verbose:
                sys.stderr.write(
                    f"INFO: fingerprint of {url} for OIDC provider {name} already in thumbprint list\n"
                )
            return

        if self.verbose:
            subject = public_key.subject.rfc4514_string()
            issuer = public_key.issuer.rfc4514_string()
            sys.stderr.write(
                f"INFO: updating fingerprint of {url} for OIDC provider {name}, {subject} issued by {issuer}\n"
            )

        sys.stderr.write(
            f"INFO: updating fingerprint of {url}, for OIDC provider {name} to {fingerprint}, valid until {public_key.not_valid_after_utc}\n"
        )
        self.dirty = True

        if not isinstance(thumbprints, CommentedSeq):
            new_thumbprints = CommentedSeq()
            if self.append:
                new_thumbprints.extend(thumbprints)
            thumbprints = new_thumbprints

        thumbprints.append(fingerprint)
        thumbprints.yaml_add_eol_comment(
            f"valid until {public_key.not_valid_after_utc}", len(thumbprints) - 1
        )
        provider["Properties"]["ThumbprintList"] = thumbprints


@click.command(
    name="oidc-provider-thumbprints", help=OIDCProviderThumbprintsUpdater.__doc__
)
@click.option("--url", required=False, type=str, help="of the OIDC provider to update")
@click.option("--append", required=False, is_flag=True, help="append the fingerprint")
@click.argument("path", nargs=-1, required=True, type=click.Path(exists=True))
@click.pass_context
def update_oidc_provider_thumbprint(ctx, url, append, path):
    updater = OIDCProviderThumbprintsUpdater()
    updater.main(url, append, list(path), ctx.obj["dry_run"], ctx.obj["verbose"])
