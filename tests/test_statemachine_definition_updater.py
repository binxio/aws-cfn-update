from aws_cfn_update.statemachine_updater import StateMachineDefinitionUpdater
import json


sample = {
    "Resources": {
        "Machine1": {
            "Type": "AWS::StepFunctions::StateMachine",
            "Properties": {"DefinitionString": ""},
        },
        "Machine2": {"Type": "AWS::StepFunctions::StateMachine"},
    }
}


def test_replace_body():
    updater = StateMachineDefinitionUpdater()
    updater.resource_name = "Machine1"
    updater.template = json.loads(json.dumps(sample))
    updater.definition = '{ "hello world": "1" }'

    updater.update_template()
    assert updater.dirty
    definition = updater.template["Resources"]["Machine1"]["Properties"].get(
        "DefinitionString"
    )
    assert isinstance(definition, dict)
    assert definition.get("Fn::Sub") == updater.definition

    updater.resource_name = "Machine2"
    updater.with_fn_sub = False
    updater.update_template()
    assert updater.dirty
    definition = updater.template["Resources"]["Machine2"]["Properties"].get(
        "DefinitionString"
    )
    assert isinstance(definition, str)
    assert definition == updater.definition
