# aws-cfn-update

Programmatically update CloudFormation templates. It will update both .yaml and .json formats of
a CloudFormation template. Note that formatting and comments may be lost.

Commands:

```
  add-new-resources          Add resources that exist in the new template and not in the existing template.
  remove-resource            Removes the specified CloudFormation resource and all resources that reference it.

  container-image            Updates the Docker image of ECS Container Definitions.

  lambda-inline-code         Updates the inline code of an AWS::Lambda::Function resource.
  config-rule-inline-code    Updates the inline code of an AWS::Config::ConfigRule resource.
  rest-api-body              Updates the body of a REST API Resource, with an standard Open API specification merged with AWS API Gateway extensions.
  state-machine-definition   Updates the definition of an AWS::StepFunctions::StateMachine.
  lambda-s3-key              Updates the S3Key entry of a Lambda Function definition.

  cron-schedule-expression   Updates the schedule expression of an AWS::Events::Rules resources to reflect the scheduled time in UTC.
  oidc-provider-thumbprints  Updates the thumbprints list of an AWS::IAM::OIDCProvider.

  latest-ami                 Updates the AMI name of Custom::AMI resources to the latest version.
  packer-latest-ami          Updates a packer.json source_ami_filter to the latest AMI version.

```

# remove-resource - removes the specified resource and all referencing resources

will remove the specified resource and all the references. For example, the command:
```
aws-cfn-update remove-resource --resource AMI .
```
will update:

```yaml
Resources:
  AMI:
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Ref AMI
  AMIv2:
    Type: Custom::AMI
```

to:

```yaml
Resources:
  AMIv2:
    Type: Custom::AMI
```

# add-new-resources - adds new resources from another template

will add missing parameters, conditions, mappings and resources from another template to this template. For example, given the following
template:
```
Parameters:
  Vpc:
    Type: String
Resources:
  AMI:
    Type: Custom::AMI
  AMIv2:
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Ref AMI
```
The following command:
```
aws-cfn-update add-new-resources --source new.yaml old.yaml
```

will update old.yaml:

```yaml
Resources:
  AMI:
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Ref AMI
```

to:

```yaml
Parameters:
  Vpc:
    Type: String
Resources:
  AMI:
    Type: Custom::AMI
  AMIv2:
    Type: Custom::AMI
  EC2Instance:
    ImageId: !Ref AMI
```


# container-image - Updates the Docker image of ECS Container Definitions.

will update any container definition where the base image name matches the specified image name
excluding the tag. For example, the command:
```
aws-cfn-update container-image --image mvanholsteijn/paas-monitor:0.6.0
```
will update:

```yaml
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
        Image: mvanholsteijn/paas-monitor:0.5.9
```

to::

```yaml
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
        Image: mvanholsteijn/paas-monitor:0.6.0
```

The environment variable AWS_CFN_UPDATE_CONTAINER_IMAGES can be used to specify a
whitespace separated list of container images to update.

# latest-ami - Updates the AMI name of Custom::AMI resources

will update the AMI name of [Custom::AMI](https://github.com/binxio/cfn-ami-provider) resources to the latest version.

For example, the command:

```
aws-cfn-update latest-ami --ami-name-pattern 'amzn-ami-*ecs-optimized'
```

Updates the AMI name of Custom::AMI resources to the latest version.
It will update the following resource definition from:

```yaml
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
```
to:

```yaml
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.l-amazon-ecs-optimized
           Owners:
             - amazon
```

By specifying --add-new-version, a new Custom::AMI will be added
to the template with a new name. A suffix `v<version>` is appended
to create the new resource. The highest reference to the Custom::AMI
resource is replaced. It will change:

```yaml
      CustomAMI:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv2:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.b-amazon-ecs-optimized
           Owners:
             - amazon
      Instance:
         Type: AWS::EC2::Instance
         Properties:
            ImageId: !Ref CustomAMIv2
Outputs:
  OldestAMI:
    Value: !Ref CustomAMI
```
to:

```yaml
      CustomAMI:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.a-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv2:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.b-amazon-ecs-optimized
           Owners:
             - amazon
      CustomAMIv3:
         Type: Custom::AMI
         Properties:
           Filters:
             name: amzn-ami-2017.09.l-amazon-ecs-optimized
           Owners:
             - amazon
      Instance:
         Type: AWS::EC2::Instance
         Properties:
            ImageId: !Ref CustomAMIv3		# <--- updated this
Outputs:
  OldestAMI:
    Value: !Ref CustomAMI			# <-- unchanged
```


# container-image - Updates the Docker image of ECS Container Definitions.
Updates the schedule expression of an AWS::Events::Rules resources to
reflect the scheduled time in UTC. The required cron rule is taken
from the description. It will update the following resource definition from:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 01 * * ? *)
    State: ENABLED
```

to:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 23 * * ? *)
    State: ENABLED
```

with --timezone Europe/Amsterdam and --date 2018-08-01. If the updater is
run with --date 2018-12-01, it will change it to:

```
DailyTaskSchedule:
  Type: AWS::Events::Rule
  Properties:
    Description: run daily - cron(30 01 * * ? *)
    Name: run daily
    ScheduleExpression: cron(30 00 * * ? *)
    State: ENABLED
```

# rest-api-body - update the body of an AWS::ApiGateway::RestApi

Updates the body of a REST API Resource, with an standard Open API
specification merged with AWS API Gateway extensions.

If you specify --add-new-version, it will create a new version of the
resource and update all references to it. This will enforce the deployment
of the new api.

If you want to keep the previous definition, specify --keep to a value of
2 or higher. This might be handy if you have old clients still accessing
the old version of the API.

If no changes are detected, no changes are made. Please make sure that all
dictionary keys in th specifications are strings, not integers (especially
the case with `responses`). When updating json CFN templates, the compare
algorithm does not work properly.

```
Options:
  --resource TEXT                AWS::ApiGateway::RestApi body to update [required]
  --open-api-specification PATH  defining the interface  [required]
  --api-gateway-extensions PATH  to add the the specification  [required]
  --add-new-version              of the RestAPI resource and replace all references
  --keep INTEGER                 number of versions to keep, if --add-new-version is specified
```

# lambda-inline-code - updates the inline code of an AWS::Lambda::Function resource.

Update the inline code of an AWS::Lambda::Function to include the content of the
specified file.  It changes:

```
    ELBListenerRuleProvider:
      Type: AWS::Lambda::Function
      Function: cfn-listener-rule-provider
```
into:
```
    ELBListenerRuleProvider:
      Type: AWS::Lambda::Function
      Properties:
        Code:
          ZipFile:
            import boto3
            import cfnresponse
            ELB = boto3.client('elbv2')
            ...
        Function: cfn-listener-rule-provider
```

# lambda-s3-key - updates the S3Key entry of a Lambda Function definition

Updates the S3Key entry of a Lambda Function definition. The s3 key must be
a semver key name in the format <prefix><semver>.zip: For example:

```shell
aws-cfn-update lambda-s3-key --s3-key lambdas/iam-sudo-0.3.1.zip
```

will change:

```yaml
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function
        Properties:
          Code:
            S3Bucket: !Sub 'binxio-public-${AWS::Region}'
            S3Key: lambdas/iam-sudo-0.1.0.zip
```
into:

```yaml
      ELBListenerRuleProvider:
        Type: AWS::Lambda::Function
        Properties:
          Code:
            S3Bucket: !Sub 'binxio-public-${AWS::Region}'
            S3Key: lambdas/iam-sudo-0.3.1.zip
              ...
```

The environment variable AWS_CFN_UPDATE_LAMBDA_S3_KEYS can be used to specify a
whitespace separated list of S3 keys to update.

# config-rule-inline-code - updates the inline code of an AWS::Config::ConfigRule resource.

Update the inline code of an AWS::Config::ConfigRule to include the content of the
specified file. When executing:

```shell
aws-cfn-update config-rule-inline-code --resource ConfigRule --file ./rules/my-rule.guard template.yaml
```
It changes:
```
    ConfigRule:
      Type: AWS::Config::ConfigRule
      Properties:
        Source:
          Owner: CUSTOM_POLICY
          CustomPolicyDetails:
            EnableDebugLogDelivery: true
            PolicyRuntime: guard-2.x.x
```
into:
```
    ConfigRule:
      Type: AWS::Config::ConfigRule
      Properties:
        Source:
          Owner: CUSTOM_POLICY
          CustomPolicyDetails:
            EnableDebugLogDelivery: true
            PolicyRuntime: guard-2.x.x
            PolicyText: |
              rule name when resourceType == "AWS::S3::Bucket" {
                  ...
              }
            ...
```

# state-machine-definition - updates the definition string of an AWS::StepFunctions::StateMachine

Updates the definition of an AWS::StepFunctions::StateMachine.

The definition is read from the file specified by --definition. By
default, the content will be passed into the Fn::Sub function to allow
references to parameters and resource attributes in the template.

If you do not want substitution for your definition, specify --no-fn-sub.

```
Options:
  --resource TEXT         AWS::StepFunctions::StateMachine definition to
                          update  [required]
  --definition PATH       of the state machine  [required]
  --fn-sub / --no-fn-sub  for the definition
  --help                  Show this message and exit.
```

For an example, check out [./samples/state-machine-definition](./samples/state-machine-definition)

# oidc-provider-thumbprints - updates the thumbprints list of an AWS::IAM::OIDCProvider.

By default, it updates the thumbprints of all OIDCProviders specified
templates. Optionally, you can specify a specific OIDC provider.

```
Options:
  --url TEXT  of the OIDC provider to update, or all if not specified
  --append    append the fingerprint
  --help      Show this message and exit.
```

# Installation

Simply run:

```bash
pip install aws-cfn-update
```


# Usage

To use it:
```bash
aws-cfn-update --help
```

