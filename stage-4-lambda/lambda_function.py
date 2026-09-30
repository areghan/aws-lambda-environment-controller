import json
import boto3


ssm = boto3.client("ssm")
ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    # Read configuration from Parameter Store
    instance_parameter = ssm.get_parameter(
        Name="/lambda-environment-controller/dev/instance-id"
    )

    action_parameter = ssm.get_parameter(
        Name="/lambda-environment-controller/dev/action"
    )

    instance_id = instance_parameter["Parameter"]["Value"]
    action = action_parameter["Parameter"]["Value"].lower()

    print(f"Instance ID: {instance_id}")
    print(f"Requested action: {action}")

    # Validate the requested action
    if action not in ["start", "stop"]:
        raise ValueError(
            f"Invalid action: {action}. Expected 'start' or 'stop'."
        )

    # Perform the requested EC2 action
    if action == "start":
        response = ec2.start_instances(
            InstanceIds=[instance_id]
        )
    else:
        response = ec2.stop_instances(
            InstanceIds=[instance_id]
        )

    print(f"EC2 response: {response}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"EC2 instance {instance_id} requested to {action}",
            "instance_id": instance_id,
            "action": action
        })
    }
