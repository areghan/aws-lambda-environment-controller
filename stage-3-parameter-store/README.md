# Stage 3 - AWS Systems Manager Parameter Store

## Objective

Use AWS Systems Manager Parameter Store to store Lambda configuration outside of the application code.

The Lambda Environment Controller will retrieve:

- The EC2 instance ID
- The desired EC2 action

This prevents configuration from being hard-coded inside the Lambda function.

---

# Architecture

```text
                    AWS Lambda
                        |
                        | ssm:GetParameter
                        v
               +-------------------+
               |  Parameter Store   |
               |                   |
               | /dev/instance-id  |
               | /dev/action       |
               +---------+---------+
                         |
                         v
                  EC2 Environment
AWS Region
us-east-1
Parameter Naming Convention

Parameters use the following hierarchy:

/lambda-environment-controller/
└── dev/
    ├── instance-id
    └── action

This makes it possible to separate environments later:

/lambda-environment-controller/dev/...
/lambda-environment-controller/staging/...
/lambda-environment-controller/prod/...
Step 1 - Identify EC2 Instance

The EC2 instance was identified using the project tag:

aws ec2 describe-instances \
  --region us-east-1 \
  --filters "Name=tag:Project,Values=aws-lambda-environment-controller" \
            "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].{ID:InstanceId,Name:Tags[?Key==`Name`]|[0].Value,State:State.Name}' \
  --output table

Current instance:

Instance ID: i-0e0fb42ce4d7ed30b
Name: lambda-controller-dev
State: running
Step 2 - Create Instance ID Parameter

Command:

aws ssm put-parameter \
  --region us-east-1 \
  --name "/lambda-environment-controller/dev/instance-id" \
  --type "String" \
  --value "i-0e0fb42ce4d7ed30b" \
  --description "EC2 instance controlled by the development Lambda environment controller"

Result:

Version: 1
Tier: Standard
Step 3 - Retrieve Instance ID

Command:

aws ssm get-parameter \
  --region us-east-1 \
  --name "/lambda-environment-controller/dev/instance-id" \
  --query 'Parameter.{Name:Name,Type:Type,Value:Value,Version:Version}' \
  --output table

Result:

Name: /lambda-environment-controller/dev/instance-id
Type: String
Value: i-0e0fb42ce4d7ed30b
Version: 1
Step 4 - Create Action Parameter

The desired EC2 action is stored separately from the Lambda code.

Command:

aws ssm put-parameter \
  --region us-east-1 \
  --name "/lambda-environment-controller/dev/action" \
  --type "String" \
  --value "stop" \
  --description "Desired EC2 action for the development environment controller"

Result:

Version: 1
Tier: Standard
Step 5 - Retrieve Both Parameters

Command:

aws ssm get-parameters \
  --region us-east-1 \
  --names \
    "/lambda-environment-controller/dev/instance-id" \
    "/lambda-environment-controller/dev/action" \
  --query 'Parameters[].{Name:Name,Type:Type,Value:Value,Version:Version}' \
  --output table

Current configuration:

instance-id → i-0e0fb42ce4d7ed30b
action      → stop
Standard vs SecureString

The parameters created in this stage use:

Type: String

The EC2 instance ID and desired action are not secrets.

For sensitive configuration such as:

Passwords
API keys
Database credentials
Tokens

we would use:

SecureString

and protect the value using AWS KMS.

IAM Requirement

The Lambda execution role created in Stage 2 contains:

ssm:GetParameter

This allows Lambda to retrieve configuration from Parameter Store.

Why Parameter Store?

Without Parameter Store:

INSTANCE_ID = "i-0e0fb42ce4d7ed30b"
ACTION = "stop"

With Parameter Store:

Lambda
   |
   +-- Get instance ID
   |
   +-- Get desired action
   |
   v
EC2

Configuration can therefore be changed without changing the Lambda source code.

Current Parameters
Parameter	Value	Type
/lambda-environment-controller/dev/instance-id	i-0e0fb42ce4d7ed30b	String
/lambda-environment-controller/dev/action	stop	String
Stage 3 Result

Parameter Store successfully configured.

Status:

COMPLETE

The Lambda function will use these parameters in Stage 4.
