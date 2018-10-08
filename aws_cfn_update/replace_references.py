import re
from aws_cfn_update.cfn_updater import Ref

def replace_references(template, old_reference, new_reference):
    """
    replaces CloudFormation references { "Ref": old_reference } with { "Ref": new_reference } in `template`.
    """
    if isinstance(template, dict):
        for name, value in template.items():
            if name == 'Ref' and value == old_reference:
                template['Ref'] = new_reference
            elif isinstance(value, Ref) and value.reference == old_reference:
                value.reference = new_reference
            else:
                replace_references(template[name], old_reference, new_reference)
    elif isinstance(template, list):
        for i, value in enumerate(template):
            replace_references(value, old_reference, new_reference)
    else:
        pass # a primitive, no recursive required.
