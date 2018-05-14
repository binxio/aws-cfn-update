
def replace_references(template, old_reference, new_reference):
    """
    replaces CloudFormation references { "Ref": old_reference } with { "Ref": new_reference } in `template`.
    """
    if isinstance(template, dict):
        for name in list(template.keys()):
            if name == 'Ref' and template[name] == old_reference:
                template['Ref'] = new_reference
            else:
                replace_references(template[name], old_reference, new_reference)
    elif isinstance(template, list):
        for i, value in enumerate(template):
            replace_references(value, old_reference, new_reference)
    else:
        pass # a primitive, no recursive required.
