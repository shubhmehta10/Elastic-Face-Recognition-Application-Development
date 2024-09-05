import os
import boto3
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)
res = dict()

# aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region_name = "us-east-1"

req_queue = "https://sqs.us-east-1.amazonaws.com/381492304139/1230683898-req-queue"
resp_queue = "https://sqs.us-east-1.amazonaws.com/381492304139/1230683898-resp-queue"

sqs_client = boto3.client(
    "sqs",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

@app.route("/", methods=["POST"])
def upload_image():
    if "inputFile" not in request.files:
        return jsonify({"error": "File not provided"}), 400
    
    image = request.files["inputFile"]
    im = image.read()
    f_name = os.path.splitext(image.filename)[0]
    encoded_msg = base64.b64encode(im).decode("ascii")
    
    message_body = f"{f_name} {encoded_msg}"
    
    try:
        response = sqs_client.send_message(QueueUrl=req_queue, MessageBody=message_body)
        return jsonify({"message": f"Image {f_name} uploaded successfully", "response": response}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_correct_output(image_name):
    try:
        response = sqs_client.receive_message(
            QueueUrl=resp_queue,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=20, 
            MessageAttributeNames=['All']
        )
        
        if "Messages" in response:
            for msg in response["Messages"]:
                msg_body = msg["Body"]
                parts = msg_body.split(" ", 1) 
                
                if parts[0] == image_name and len(parts) > 1:
                    sqs_client.delete_message(QueueUrl=resp_queue, ReceiptHandle=msg["ReceiptHandle"])
                    res[parts[0]] = parts[1]
                    return parts[1]
                
        return "Result not found or image name mismatch."
    except Exception as e:
        print(f"Error fetching output: {e}")
        return "Error processing request."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
