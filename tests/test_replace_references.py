from aws_cfn_update.replace_references import replace_references
from aws_cfn_update.cfn_updater import yaml
from io import StringIO


def test_simple():
    template = {'Ref': 'Old'}
    replace_references(template, 'Old', 'New')
    assert template['Ref'] == 'New'

    template = {'DependsOn': [{'Ref': 'Old'}]}
    replace_references(template, 'Old', 'New')
    assert template['DependsOn'][0]['Ref'] == 'New'

    template = 'Old'
    replace_references(template, 'Old', 'New')
    assert template == 'Old'

def test_yaml():
    template = yaml.load('AMI: !Ref Old')
    replace_references(template, 'Old', 'New')

    result = StringIO()
    yaml.dump(template, result)
    assert result.getvalue() == 'AMI: !Ref New\n'
