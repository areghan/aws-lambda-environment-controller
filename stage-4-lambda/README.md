# Stage 4 — AWS Lambda Environment Controller

## Objective

Create an AWS Lambda function using Python and boto3 to control the
development EC2 environment based on configuration stored in AWS
Systems Manager Parameter Store.

The Lambda can start or stop the EC2 instance without changing the
Lambda source code.

---

## Architecture

Parameter Store
      |
      | Get instance ID and desired action
      v
AWS Lambda
      |
      | boto3
      v
Amazon EC2
      |
      v
CloudWatch Logs

---

## Lambda Configuration

Function name:

    LambdaEnvironmentController

Runtime:

    Python 3.14

Handler:

    lambda_function.lambda_handler

Memory:

    128 MB

Timeout:

    10 seconds

IAM execution role:

    lambda-environment-controller-role

Region:

    us-east-1

---

## Parameter Store Configuration

Instance parameter:

    /lambda-environment-controller/dev/instance-id

Current value:

    i-0e0fb42ce4d7ed30b

Action parameter:

    /lambda-environment-controller/dev/action

The action parameter supports:

    start
    stop

The action parameter was tested with both values.

---

## Lambda Source Code

The Lambda uses boto3 to:

1. Retrieve the EC2 instance ID from Parameter Store.
2. Retrieve the desired action from Parameter Store.
3. Validate the requested action.
4. Start or stop the EC2 instance.
5. Log the operation to CloudWatch.
6. Return a JSON response.

---

## Deployment

The Lambda deployment package was created as:

    lambda-environment-controller.zip

The ZIP file is intentionally excluded from Git using .gitignore.

---

## Testing

### Test 1 — Stop EC2

Parameter Store:

    action = stop

Lambda was invoked using:

    aws lambda invoke \
      --region us-east-1 \
      --function-name LambdaEnvironmentController \
      --payload '{}' \
      response.json

Result:

    statusCode = 200
    action = stop

EC2 changed from:

    running -> stopped

---

### Test 2 — Start EC2

Parameter Store was changed from:

    stop

to:

    start

The parameter version changed from:

    Version 1 -> Version 2

The Lambda source code was not changed or redeployed.

The same Lambda function was invoked again.

Result:

    statusCode = 200
    action = start

EC2 changed from:

    stopped -> running

This demonstrates that the Lambda is configuration-driven.

---

## CloudWatch Logs

Lambda automatically writes execution logs to:

    /aws/lambda/LambdaEnvironmentController

The logs confirmed:

    Instance ID: i-0e0fb42ce4d7ed30b
    Requested action: stop

The EC2 API returned HTTPStatusCode 200.

The Lambda was subsequently tested with:

    Requested action: start

---

## AWS Services Used

- AWS Lambda
- Amazon EC2
- AWS Systems Manager Parameter Store
- AWS IAM
- Amazon CloudWatch Logs
- AWS CLI

---

## Skills Practised

- Python Lambda development
- boto3
- Lambda execution roles
- IAM permissions
- Parameter Store
- EC2 API operations
- CloudWatch logging
- AWS CLI
- JSON
- Lambda deployment packages
- Configuration-driven automation

---

## Stage Status

Stage 4: COMPLETE

The Lambda has successfully demonstrated:

    Parameter Store -> Lambda -> EC2

for both:

    START
    STOP
