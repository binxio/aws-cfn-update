# aws-cfn-update

Programmatically update CloudFormation templates.

Commands:
```
  container-image  Updates the Docker image of ECS Container...
  latest-ami       Updates the AMI name of Custom::AMI resources...
```


# Updates the Docker image of ECS Container Definitions.

aws-cfn-update container-image will update any container definition 
where the base image name matches the specified image name 
excluding the tag.

For example, an image name of `mvanholsteijn/paas-monitor:0.6.0` will
update:

```
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
	Image: mvanholsteijn/paas-monitor:0.5.9
```

to::

```
  Type: AWS::ECS::TaskDefinition
  Properties:
    ContainerDefinitions:
      - Name: paas-monitor
	Image: mvanholsteijn/paas-monitor:0.6.0
```



# Updates the AMI name of Custom::AMI resources

`aws-cfn-update` `latest-ami` will update the AMI name of 
Custom::AMI resources to the latest version.  

For example, an ami-name-pattern of `amzn-ami-*ecs-optimized` will update
the following resource definition from::

```
   Type: Custom::AMI
   Properties:
     Filters:
       name: amzn-ami-2013.09.a-amazon-ecs-optimized
```

to::

```
   Type: Custom::AMI
   Properties:
     Filters:
       name: amzn-ami-2017.09.l-amazon-ecs-optimized
```


# Installation

Simply run:

```
    $ pip install aws-cfn-update
```


# Usage

To use it:

    $ aws-cfn-update --help

