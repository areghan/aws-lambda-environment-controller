# Stage 2 - IAM

## Objective

Create a secure IAM execution role for the AWS Lambda Environment Controller.

The role follows the principle of least privilege and allows Lambda to:

- Discover EC2 instances
- Start EC2 instances
- Stop EC2 instances
- Read configuration from Systems Manager Parameter Store
- Write logs to CloudWatch Logs

---

# IAM Architecture

```text
AWS Lambda
     |
     | sts:AssumeRole
     v
lambda-environment-controller-role
     |
     v
lambda-environment-controller-policy
     |
     +-- EC2
     |   +-- ec2:DescribeInstances
     |   +-- ec2:StartInstances
     |   +-- ec2:StopInstances
     |
     +-- Parameter Store
     |   +-- ssm:GetParameter
     |
     +-- CloudWatch Logs
         +-- logs:CreateLogGroup
         +-- logs:CreateLogStream
         +-- logs:PutLogEvents
Step 1 - Trust Policy

Created:

policies/lambda-trust-policy.json

Contents:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
Purpose

The trust policy determines who is allowed to assume the role.

In this project, AWS Lambda is the trusted service.

The important configuration is:

"Principal": {
  "Service": "lambda.amazonaws.com"
}

and:

"Action": "sts:AssumeRole"
Step 2 - Create IAM Role

Role name:

lambda-environment-controller-role

Command:

aws iam create-role \
  --role-name lambda-environment-controller-role \
  --assume-role-policy-document file://policies/lambda-trust-policy.json \
  --description "Execution role for the AWS Lambda Environment Controller"
Role ARN
arn:aws:iam::764416828658:role/lambda-environment-controller-role
Verification
aws iam get-role \
  --role-name lambda-environment-controller-role \
  --query 'Role.{RoleName:RoleName,Arn:Arn,CreateDate:CreateDate}' \
  --output table

Step 3 - Permissions Policy

Created:

policies/lambda-permissions-policy.json

Contents:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EC2EnvironmentControl",
      "Effect": "Allow",
      "Action": [
        "ec2:DescribeInstances",
        "ec2:StartInstances",
        "ec2:StopInstances"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ParameterStoreRead",
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudWatchLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}

JSON validation

Validated locally with:

python3 -m json.tool policies/lambda-permissions-policy.json

The JSON was valid.


Step 4 - Create Customer-Managed Policy

Command:

aws iam create-policy \
  --policy-name lambda-environment-controller-policy \
  --policy-document file://policies/lambda-permissions-policy.json \
  --description "Least-privilege permissions for the Lambda Environment Controller"

Policy name:

lambda-environment-controller-policy

Policy ARN:

arn:aws:iam::764416828658:policy/lambda-environment-controller-policy

Policy ID:

ANPA3D6WLETZOX7RBINDM

Step 5 - Attach Policy to Role

Command:

aws iam attach-role-policy \
  --role-name lambda-environment-controller-role \
  --policy-arn arn:aws:iam::764416828658:policy/lambda-environment-controller-policy
Verification
aws iam list-attached-role-policies \
  --role-name lambda-environment-controller-role \
  --output table

Expected policy:

lambda-environment-controller-policy
Step 6 - Verify Trust Relationship

Command:

aws iam get-role \
  --role-name lambda-environment-controller-role \
  --query 'Role.AssumeRolePolicyDocument' \
  --output json

Expected trusted service:

lambda.amazonaws.com
Least Privilege

The Lambda role does NOT have:

AdministratorAccess

Instead it has only the permissions currently required by the application.

Required permissions:

EC2:
    ec2:DescribeInstances
    ec2:StartInstances
    ec2:StopInstances

Parameter Store:
    ssm:GetParameter

CloudWatch Logs:
    logs:CreateLogGroup
    logs:CreateLogStream
    logs:PutLogEvents

