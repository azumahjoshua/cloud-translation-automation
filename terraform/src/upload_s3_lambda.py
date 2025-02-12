import json
import boto3
import base64
import os
import uuid

s3_client = boto3.client("s3")
lambda_client = boto3.client("lambda")

TRANSLATION_INPUT_BUCKET_NAME = os.environ.get("TRANSLATION_INPUT_BUCKET_NAME")
TRANSLATION_LAMBDA_NAME = os.environ.get("TRANSLATION_LAMBDA_NAME")

def lambda_handler(event, context):
    try:
        content_type = event["headers"].get("Content-Type", "")
        file_content = None
        file_name = None

        if content_type == "application/json":
            body = json.loads(event["body"])
            file_content = base64.b64decode(body["file_data"])
            file_name = body.get("file_name", f"uploaded_file_{uuid.uuid4().hex}.json")
        
        elif "multipart/form-data" in content_type:
            body = event["body"]
            file_name = event["headers"].get("X-File-Name", f"uploaded_file_{uuid.uuid4().hex}.json")
            file_content = base64.b64decode(body)
        
        else:
            return {"statusCode": 400, "body": json.dumps({"error": "Unsupported content type"})}
        
        # Ensure file content is valid
        if not file_content:
            return {"statusCode": 400, "body": json.dumps({"error": "Invalid or empty file content"})}
        
        # Generate S3 object key
        s3_object_key = f"uploads/{file_name}"
        print(f"Uploading file: {file_name} to S3 at {s3_object_key}")
        
        # Upload file to S3
        s3_client.put_object(Bucket=TRANSLATION_INPUT_BUCKET_NAME, Key=s3_object_key, Body=file_content)
        
        # Invoke translation Lambda asynchronously
        lambda_client.invoke(
            FunctionName=TRANSLATION_LAMBDA_NAME,
            InvocationType="Event",  # Async execution
            Payload=json.dumps({"s3_key": s3_object_key})
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File uploaded and translation started",
                "s3_key": s3_object_key
            })
        }
    except Exception as e:
        print(f"Error in Lambda handler: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
