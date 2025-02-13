import json
import boto3
import base64
import os
import uuid

# AWS Clients
s3_client = boto3.client("s3")

# Environment Variables
TRANSLATION_INPUT_BUCKET_NAME = os.environ.get("TRANSLATION_INPUT_BUCKET_NAME")

def upload_file_to_s3(file_content, file_name=None):
    """Uploads a file to S3 and returns the S3 object key."""
    try:
        if not file_name:
            file_name = f"uploaded_file_{uuid.uuid4().hex}.json"

        s3_object_key = f"uploads/{file_name}"
        print(f"Uploading file: {file_name} to S3 at {s3_object_key}")

        # Upload file to S3
        s3_client.put_object(Bucket=TRANSLATION_INPUT_BUCKET_NAME, Key=s3_object_key, Body=file_content)

        return s3_object_key
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None

def decode_file_content(event):
    """Decodes the uploaded file content from the request."""
    try:
        content_type = event["headers"].get("Content-Type", "")
        file_content = None
        file_name = None

        if content_type == "application/json":
            body = json.loads(event["body"])
            file_content = base64.b64decode(body["file_data"])
            file_name = body.get("file_name")

        elif "multipart/form-data" in content_type:
            body = event["body"]
            file_name = event["headers"].get("X-File-Name")
            file_content = base64.b64decode(body)

        if not file_content:
            raise ValueError("Invalid or empty file content")

        return file_content, file_name
    except Exception as e:
        print(f"Error decoding file content: {e}")
        return None, None
