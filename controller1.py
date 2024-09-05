import boto3
import os
import math
import time

sqs_queue = boto3.client(
    "sqs",
    region_name="us-east-1",
    # aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    # aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
)

ec2 = boto3.client(
    "ec2",
    region_name="us-east-1",
#     aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
#     aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# )

zero_instances = False
zero_time = time.time()

def run():
    global zero_instances
    global zero_time

    req_queue = "https://sqs.us-east-1.amazonaws.com/381492304139/1230683898-req-queue"

    input_queue_attributes = sqs_queue.get_queue_attributes(
        QueueUrl=req_queue, AttributeNames=["ApproximateNumberOfMessages"]
    )
    approx_num_messages = int(
        input_queue_attributes["Attributes"]["ApproximateNumberOfMessages"]
    )

    running_ec2 = ec2.describe_instances(
        Filters=[
            {"Name": "instance-state-name", "Values": ["running", "pending"]},
            {"Name": "tag:tier", "Values": ["app"]},
        ]
    )

    running_ec2_ids = []

    if running_ec2["Reservations"]:
        for res in running_ec2["Reservations"]:
            for instance in res["Instances"]:
                running_ec2_ids.append(instance["InstanceId"])
    print(approx_num_messages, running_ec2_ids)

    messages_per_instance = (
        5
    )

    required_ec2_instances = min(
        math.ceil(approx_num_messages / messages_per_instance), 20
    )
    print("required = " + str(required_ec2_instances))

    num_current_ec2_running = len(running_ec2_ids)
    print("running = " + str(num_current_ec2_running))

    
    if required_ec2_instances == 0 and num_current_ec2_running > 0:
        if zero_instances:
            mins = (time.time() - zero_time) // 60
            if mins < 1:
                required_ec2_instances = 1
        else:
            zero_time = time.time()
            zero_instances = True
            required_ec2_instances = 1
        print("New required count: " + str(required_ec2_instances))
    elif zero_instances and required_ec2_instances > 0:
        zero_instances = False

    user_data = """#!/bin/bash 
    sudo -u ubuntu -i <<'EOF'
    python3 /home/ubuntu/CSE546-Cloud-Computing/model/face_recognition.py
    EOF"""

    if num_current_ec2_running == required_ec2_instances:
        print("Autoscaling not required!")
    elif num_current_ec2_running > required_ec2_instances:
        remove = num_current_ec2_running - required_ec2_instances
        print(ec2.terminate_instances(InstanceIds=running_ec2_ids[:remove]))
    else:
        add = required_ec2_instances - num_current_ec2_running
        response = ec2.run_instances(
            ImageId="ami-086b8cecb7133d863", 
            InstanceType="t2.micro",
            KeyName="cc_key_pair",
            MinCount=add,
            MaxCount=add,
            UserData=user_data,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "tier", "Value": "app"},
                        {"Key": "Name", "Value": "app-tier"},
                    ],
                },
            ],
        )
        print(response)


if __name__ == "__main__":
    while True:
        run()
        time.sleep(10)
