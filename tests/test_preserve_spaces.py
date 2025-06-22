from aws_cfn_update.replace_references import replace_references
from aws_cfn_update.cfn_updater import CfnUpdater
from io import StringIO
import textwrap


def test_preserve_comment():
    yaml = CfnUpdater().yaml

    input = "---\n# comments are great!\nResources:\nAMI: !Ref Old\n"

    template = yaml.load(input)
    result = StringIO()
    yaml.dump(template, result)
    output = result.getvalue()

    print("")
    print(input)
    print(output)
    assert output == input


def test_preserve_indent():
    yaml = CfnUpdater().yaml

    input = textwrap.dedent(
        """\
        ---
        Resources:
          Type:  # array
            - A
            - B
            - C
        """
    )

    template = yaml.load(input)
    result = StringIO()
    yaml.dump(template, result)
    output = result.getvalue()

    assert output == input


def test_preserved_tagged_array():
    yaml = CfnUpdater().yaml

    input = textwrap.dedent(
        """\
        ---
        Resources:
          Type: !Sub
            - '${B}-{A}'
            - B: Hello
              C: World
        """
    )

    template = yaml.load(input)
    result = StringIO()
    yaml.dump(template, result)
    output = result.getvalue()

    assert output == input


def test_nested_tagged_sequence_indentation():
    """
    test whether the indent of nested sequences is 4 spaces instead of 2. This is a quirk of Ruamel yaml.
    """
    input = textwrap.dedent(
        """\
    ---
    Resources:
      KongRouteCors:
        Type: Custom::KongPlugin

        Properties:
          Plugin:
            name: cors
            route:
              id: !GetAtt 'KongRoute.id'
            protocols:
              - http
              - https
            config:
              origins:
                - !Sub 'https://${ExternalDomainName}'
                - !If
                    - IsDevEnv
                    - http://localhost:3000
                    - !Ref 'AWS::NoValue'
                - !If
                    - IsDevEnv
                    - !Sub
                        - 'https://${PortalExternalDomainName}'
                        - PortalExternalDomainName: pipodeclown.nl
                    - !Ref 'AWS::NoValue'
              methods:
                - GET
                - PUT
                - POST
                - DELETE
                - PATCH
                - OPTIONS
      """
    )
    yaml = CfnUpdater().yaml

    template = yaml.load(input)
    result = StringIO()
    yaml.dump(template, result)
    output = result.getvalue()
    assert output == input
