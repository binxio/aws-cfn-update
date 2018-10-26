"""
A Custom CloudFormation provider supporting the latest version of
AWS::ElasticLoadBalancingV2::ListenerRule.
"""
import boto3

import cfnresponse

ELB = boto3.client('elbv2')


def lambda_handler(event, context):
    """
    Implements the Custom CloudFormation Resource interface
    """
    arn = None
    try:
        method, arn, kwargs = get_arguments(event)
        if method == 'create_rule':
            response = ELB.create_rule(**kwargs)
            arn = response['Rules'][0]['RuleArn']
        elif method == 'modify_rule':
            ELB.modify_rule(**kwargs)
        elif method == 'delete_rule':
            try:
                ELB.delete_rule(**kwargs)
            except Exception as error:
                print('{}'.format(error))

        return cfnresponse.send(event, context, cfnresponse.SUCCESS, {}, arn)
    except Exception as error:
        print('{}'.format(error))
        return cfnresponse.send(event, context, cfnresponse.FAILED, {}, arn if arn else 'failed-to-create')


def get_arguments(event):
    """
    retrieve method, ARN and resource arguments appropriate for the API
    :param event: containing the CFN request
    :return:  method, arn, arguments - for the api call of the rule
    """
    request_type = event['RequestType']
    arn = event['PhysicalResourceId'] if 'PhysicalResourceId' in event else None

    if request_type == 'Delete':
        return 'delete_rule', arn, {'RuleArn': arn}
    else:
        arguments = event['ResourceProperties'].copy()
        convert_from_string(arguments, ["Order", "Priority", "SessionTimeout"])

        if 'ServiceToken' in arguments:
            del arguments['ServiceToken']

        if is_create_required(event):
            return 'create_rule', None, arguments
        else:
            arguments['RuleArn'] = arn
            if 'ListenerArn' in arguments:
                del arguments['ListenerArn']
            if 'Priority' in arguments:
                del arguments['Priority']

        return 'modify_rule', arn, arguments


def convert_from_string(properties, fields):
    """
    convert the specified fields to native type.
    """
    for name in properties:
        if isinstance(properties[name], dict):
            convert_from_string(properties[name], fields)
        elif name in fields and isinstance(properties[name], str):
            value = str(properties[name])
            if value == 'true':
                properties[name] = True
            elif value == 'false':
                properties[name] = False
            elif value.isdigit():
                properties[name] = int(value)
            else:
                pass  # leave it a string.


def is_create_required(event):
    """
    Indicates whether a create is required in order to update.
    :param event: to check
    """
    if event['RequestType'] == 'Create':
        return True

    new = event['ResourceProperties']
    old = event['OldResourceProperties'] if 'OldResourceProperties' in event else new

    return old.get('Priority', 0) != new.get('Priority', 0) or old.get('ListenerArn', None) != new.get('ListenerArn',
                                                                                                       None)
