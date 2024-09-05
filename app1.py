import base64
from urllib import response
import boto3
from botocore.exceptions import ClientError
import os
import time
import datetime
import logging
import io


# aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = "us-east-1"


req_queue = "https://sqs.us-east-1.amazonaws.com/381492304139/1230683898-req-queue"
resp_queue = "https://sqs.us-east-1.amazonaws.com/381492304139/1230683898-resp-queue"

endpoint_url = "https://sqs.us-east-1.amazonaws.com"

s3_input_bucket = "1230683898-in-bucket"
s3_output_bucket = "1230683898-out-bucket"

logging.basicConfig(filename='app.log', level=logging.INFO)

sqs = boto3.client(
    "sqs",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    endpoint_url=endpoint_url,
    region_name=region_name,
)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

s3 = boto3.resource(
    service_name="s3",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

def receiveMessages():
    print("Receiving messages...")
    try:
        response = sqs.receive_message(
            QueueUrl=req_queue,
            AttributeNames=["SentTimestamp"],
            MaxNumberOfMessages=10,
            MessageAttributeNames=["All"],
            VisibilityTimeout=30,
            WaitTimeSeconds=10,
        )


    except Exception as e:
        print(str(e))
        return "Something went wrong"

    if "Messages" in response:
        receipt_handle = response["Messages"][0]["ReceiptHandle"]
        response1 = response["Messages"]
        deleteMessage(receipt_handle)
        return response1
    else:
        time.sleep(1)
        return receiveMessages()

def deleteMessage(receipt_handle):
    sqs.delete_message(QueueUrl=req_queue, ReceiptHandle=receipt_handle)


def decodeMessage(file_name, msg):
    decoded_msg = open(file_name, "wb")
    decoded_msg.write(base64.b64decode((msg)))
    decoded_msg.close()

def sendMessageToOutputQueue(file_name, msg):
    formatted_message = f"{file_name}:{msg}"  
    sqs.send_message(QueueUrl=resp_queue, MessageBody=formatted_message)
    logging.info(f"Sent message to output queue: {formatted_message}")

def uploadToS3InputBucket(file_name, bucket, object_name):
    try:
        response = s3_client.upload_fileobj(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def uploadToS3OutputBucket(s3, bucket_name, image_name, predicted_result):
    content = (image_name, predicted_result)
    content = " ".join(str(x) for x in content)
    s3.Object(s3_output_bucket, image_name).put(Body=content)

def initialize():
    messages = receiveMessages()

    if not messages:
        logging.info("No messages received. Waiting for new messages...")
        return

    for message in messages:
        file_name, encoded_msg = message["Body"].split()
        img_file_name = f"{file_name}.jpg"
        logging.info(f"Processing file: {img_file_name}")

        decodeMessage(img_file_name, encoded_msg)

        with open(img_file_name, "rb") as img_file:
            if uploadToS3InputBucket(img_file, s3_input_bucket, img_file_name):
                logging.info(f"Input file {img_file_name} uploaded to S3 bucket")

        # stdout = os.popen(f'"python3 D:/MS/UNIS/ASU/cloud/project1/model/face_recognition.py" + {img_file_name}')
        # result = stdout.read().strip()
        
        stdout = os.popen(f'python3 model/face_recognition.py "{img_file_name}"').read().strip()

        uploadToS3OutputBucket(s3, s3_output_bucket, file_name, stdout)
        sendMessageToOutputQueue(file_name, stdout)  # Adjusted function call here

        if os.path.exists(img_file_name):
            os.remove(img_file_name)

        deleteMessage(message['ReceiptHandle'])

        logging.info(f"Processed and responded: {file_name} with prediction: {stdout}")

if __name__ == "__main__":
    while True:
        initialize()
        time.sleep(10)