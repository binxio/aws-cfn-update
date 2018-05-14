from aws_cfn_update.replace_references import  replace_references


def test_simple():
    template = { 'Ref': 'Old'}
    replace_references(template, 'Old', 'New')
    assert template['Ref'] == 'New'

    template = {'DependsOn': [{'Ref': 'Old'}]}
    replace_references(template, 'Old', 'New')
    assert template['DependsOn'][0]['Ref'] == 'New'

    template = 'Old'
    replace_references(template, 'Old', 'New')
    assert template == 'Old'
