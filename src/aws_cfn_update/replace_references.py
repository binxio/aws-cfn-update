from ruamel.yaml.comments import TaggedScalar


def replace_references(template, old_reference, new_reference) -> bool:
    """
    replaces CloudFormation references { "Ref": old_reference } with { "Ref": new_reference } in `template`.
    returns True if one or more references where made.
    """
    result = False
    if isinstance(template, dict):
        for name, value in template.items():
            if name == "Ref" and value == old_reference:
                template["Ref"] = new_reference
                result = True
            elif (
                isinstance(value, TaggedScalar)
                and value.tag
                and value.tag.suffix == "Ref"
                and value.value == old_reference
            ):
                value.value = new_reference
                result = True
            else:
                result = (
                    replace_references(template[name], old_reference, new_reference)
                    or result
                )
    elif isinstance(template, list):
        for i, value in enumerate(template):
            result = replace_references(value, old_reference, new_reference) or result
    return result
