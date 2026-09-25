AWS Lambda Environment Controller

Hands-on AWS DevOps Practice Project

Project Overview

Build a serverless AWS Environment Controller using AWS Lambda and Python. The system will allow an operator or scheduled automation to start and stop EC2 instances based on an environment tag such as dev, uat, or prod.

Amazon EC2

AWS Lambda

IAM

AWS Systems Manager Parameter Store

Amazon EventBridge

Amazon CloudWatch

Terraform

AWS CLI

Python

Git

Architecture

                         ┌──────────────────────┐
                         │      EventBridge     │
                         │       Schedule       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        Lambda        │
                         │       Python         │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
             Parameter Store       EC2          CloudWatch
               Configuration     Start/Stop         Logs
                                    │
                              ┌─────┴─────┐
                              │           │
                            DEV          UAT
                              │
                            PROD

                         IAM controls permissions

Project Structure

aws-lambda-environment-controller/
│
├── PROJECT.md
├── stage-0-workstation/
├── stage-1-ec2/
├── stage-2-iam/
├── stage-3-parameter-store/
├── stage-4-lambda/
├── stage-5-testing/
├── stage-6-eventbridge/
└── stage-7-terraform/

Stage 0 - Workstation

Objective: prepare the local workstation and verify access to AWS.

Tools

AWS CLI: 2.36.11

Terraform: 1.15.8

Python: 3.10.12

Git: 2.34.1

AWS Region: us-east-1

AWS Identity

AWS CLI authentication was verified with:

aws sts get-caller-identity

AWS authentication: configured successfully.

Git

git init
git branch -m main

Repository initialized and default branch changed to main.

Stage 1 - EC2 Environment

Objective: create an EC2 instance that Lambda will eventually control.

AWS Region

us-east-1

VPC

Default VPC: vpc-0a688ad5b70b724cb

CIDR: 172.31.0.0/16

Subnet

Subnet: subnet-0517bf04eb411b905

Availability Zone: us-east-1a

CIDR: 172.31.0.0/20

AMI

Amazon Linux 2023

AMI: ami-0b2c9d1f3edcfd709

EC2 Instance

Instance ID: i-0e0fb42ce4d7ed30b

Instance Type: t3.micro

Environment: dev

Tags

Name        = lambda-controller-dev
Environment = dev
Project     = aws-lambda-environment-controller

Security Group

Name: lambda-controller-dev-sg

ID: sg-011f0963d27af9439

No inbound SSH access was configured because SSH is not required for the Lambda automation workload.

EC2 Discovery

The instance can be discovered using its environment tag:

aws ec2 describe-instances \
  --region us-east-1 \
  --filters "Name=tag:Environment,Values=dev" \
  --output table

Lambda will not hard-code the EC2 instance ID. Instead, it will discover instances using Environment=dev.

Stage 1 Testing

Stop EC2

aws ec2 stop-instances \
  --region us-east-1 \
  --instance-ids i-0e0fb42ce4d7ed30b

Verify

aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-0e0fb42ce4d7ed30b \
  --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name}' \
  --output table

Expected state: stopped.

Start EC2

aws ec2 start-instances \
  --region us-east-1 \
  --instance-ids i-0e0fb42ce4d7ed30b

Verify

aws ec2 describe-instances \
  --region us-east-1 \
  --instance-ids i-0e0fb42ce4d7ed30b \
  --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name}' \
  --output table

Expected state: running.

Result: successfully tested running → stopped → running.

Stage 2 - IAM

Objective: create an IAM execution role for Lambda using least privilege.

Required EC2 Permissions

ec2:DescribeInstances
ec2:StartInstances
ec2:StopInstances

Parameter Store Permission

ssm:GetParameter

CloudWatch Logs Permissions

logs:CreateLogGroup
logs:CreateLogStream
logs:PutLogEvents

Do not use AdministratorAccess. Use a dedicated Lambda execution role with only the permissions required by the application.

Stage 3 - Parameter Store

Objective: store Lambda configuration outside the Python code.

Planned parameter:

/lambda/environment-controller/config

Example configuration:

{
  "dev": {
    "enabled": true
  },
  "uat": {
    "enabled": true
  },
  "prod": {
    "enabled": false
  }
}

Lambda will retrieve this configuration using ssm:GetParameter.

Stage 4 - Lambda

Objective: build the Lambda function using Python.

Main file: lambda_function.py

Lambda Workflow

Receive Event
      ↓
Validate Action
      ↓
Validate Environment
      ↓
Read Parameter Store
      ↓
Find EC2 instances by Environment tag
      ↓
Get Instance IDs
      ↓
Start or Stop instances
      ↓
Write result to CloudWatch

Example Events

Start DEV:

{
  "action": "start",
  "environment": "dev"
}

Stop DEV:

{
  "action": "stop",
  "environment": "dev"
}

Supported Actions

start
stop

Supported Environments

dev
uat
prod

Stage 5 - Lambda Testing

Test 1 - Start DEV

{
  "action": "start",
  "environment": "dev"
}

Expected: DEV EC2 instance starts

Test 2 - Stop DEV

{
  "action": "stop",
  "environment": "dev"
}

Expected: DEV EC2 instance stops

Test 3 - Invalid Environment

{
  "action": "start",
  "environment": "production"
}

Expected: Invalid environment

Test 4 - Invalid Action

{
  "action": "delete",
  "environment": "dev"
}

Expected: Invalid action

Test 5 - No Matching Instances

{
  "action": "start",
  "environment": "uat"
}

Expected: No matching instances found if no UAT instance exists

Stage 6 - EventBridge

Objective: automate Lambda execution using schedules.

Monday-Friday
08:00
  ↓
EventBridge
  ↓
Lambda
  ↓
Start DEV

Monday-Friday
18:00
  ↓
EventBridge
  ↓
Lambda
  ↓
Stop DEV

Stage 7 - Terraform

Objective: rebuild the infrastructure using Infrastructure as Code.

Terraform Resources

IAM Role

IAM Policy

Lambda Function

CloudWatch Log Group

EventBridge Rule

EventBridge Target

Lambda Permission

Terraform Files

stage-7-terraform/
├── provider.tf
├── variables.tf
├── iam.tf
├── lambda.tf
├── eventbridge.tf
└── outputs.tf

Terraform Workflow

terraform init
terraform fmt
terraform validate
terraform plan
terraform apply
terraform destroy

Final Architecture

                         USER / SCHEDULE
                                │
                                ▼
                       ┌─────────────────┐
                       │   EventBridge   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Lambda      │
                       │     Python      │
                       └───────┬─────────┘
                               │
              ┌────────────────┼─────────────────┐
              │                │                 │
              ▼                ▼                 ▼
       Parameter Store        EC2          CloudWatch
         Configuration      Start/Stop        Logs
                               │
                    ┌──────────┴──────────┐
                    │                     │
                  DEV                    UAT
                    │
                  PROD

                         IAM
                          │
                          ▼
                  Controls permissions

DevOps Concepts Practised

AWS Lambda

Serverless architecture

EC2 automation

IAM least privilege

AWS CLI

Python

Systems Manager Parameter Store

EventBridge

CloudWatch

Infrastructure as Code

Terraform

Git

Environment tagging

Automation

Cost optimisation

Interview Explanation

I built a serverless AWS environment controller using Python and AWS Lambda. The Lambda function discovers EC2 instances using environment tags rather than hard-coded instance IDs and can start or stop the appropriate environment. Configuration is stored in Systems Manager Parameter Store, IAM follows least-privilege principles, CloudWatch provides logging, and EventBridge can trigger the Lambda on a schedule. I then reproduced the infrastructure using Terraform.

Project Progress

Stage

Status

Stage 0 - Workstation

COMPLETE

Stage 1 - EC2

COMPLETE

Stage 2 - IAM

NEXT

Stage 3 - Parameter Store

PENDING

Stage 4 - Lambda

PENDING

Stage 5 - Testing

PENDING

Stage 6 - EventBridge

PENDING

Stage 7 - Terraform

PENDING

Notes

This project is intentionally being built incrementally. Do not skip directly to Terraform. Complete the manual AWS implementation first so that the AWS services and permissions are understood before they are automated with Terraform.

AWS Lambda Environment Controller — Practice Runbook
