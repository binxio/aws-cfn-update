def add_missing_resources(template: dict, src: dict) -> bool:
    dirty = False
    for top_level in ["Parameters", "Resources", "Conditions", "Mappings"]:
        for name, value in src.get(top_level, {}).items():
            if not template.get(top_level, {}).get(name):
                if top_level not in template:
                    template[top_level] = {}
                template[top_level][name] = value
                dirty = True
    return dirty
