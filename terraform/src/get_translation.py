import json
import os
import base64
import time
import boto3
from botocore.exceptions import ClientError
from generate_translation import translate_text, handle_uploaded_file, get_cached_translation

# AWS Clients
s3_client = boto3.client("s3")

# Environment Variables
OUTPUT_BUCKET = os.environ.get("TRANSLATION_OUTPUT_BUCKET_NAME")


def handler(event, context):
    """Handles direct text translation and file uploads, returning results in JSON format."""
    try:
        print("Received event:", json.dumps(event))

        start_time = time.perf_counter()

        # Decode request body
        request = decode_request_body(event)

        if not request:
            return error_response("Invalid or empty request body")

        if "s3_key" in request:
            # File-based translation
            response_data = process_uploaded_file(request["s3_key"])
        elif "text" in request and "source_language" in request and "target_language" in request:
            # Direct text translation
            response_data = process_direct_text_translation(request)
        else:
            return error_response("Invalid request format")

        # Compute processing time
        response_data["processing_seconds"] = round(time.perf_counter() - start_time, 4)

        return success_response(response_data)

    except Exception as e:
        print(f"Lambda Error: {e}")
        return error_response(str(e))


def decode_request_body(event):
    """Decodes request body from the event, handling Base64 encoding if necessary."""
    try:
        if "body" not in event:
            return None

        if event.get("isBase64Encoded", False):
            decoded_body = base64.b64decode(event["body"]).decode("utf-8")
        else:
            decoded_body = event["body"]

        return json.loads(decoded_body)

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error decoding request body: {e}")
        return None


def process_uploaded_file(s3_key):
    """Handles file translation request using handle_uploaded_file and retrieves the translated result."""
    try:
        # Process translation
        translation_response = handle_uploaded_file(s3_key)

        if "error" in translation_response:
            return translation_response

        translated_s3_key = translation_response["s3_key"]

        # Retrieve translated content from S3
        response = s3_client.get_object(Bucket=OUTPUT_BUCKET, Key=translated_s3_key)
        translated_content = json.loads(response["Body"].read().decode("utf-8"))

        return translated_content

    except ClientError as e:
        return {"error": f"Failed to retrieve translated file: {e}"}


def process_direct_text_translation(request):
    """Handles direct text translation requests and returns JSON response."""
    text = request.get("text")
    source_lang = request.get("source_language")
    target_lang = request.get("target_language")

    if not text or not source_lang or not target_lang:
        return {"error": "Missing required fields: 'text', 'source_language', 'target_language'"}

    # Check cache first
    cached_translation = get_cached_translation(text, source_lang, target_lang)
    if cached_translation:
        return {
            "original_text": text,
            "translated_text": cached_translation,
            "source_language": source_lang,
            "target_language": target_lang,
            "cached": True
        }

    # Translate text
    translated_text = translate_text(text, source_lang, target_lang)

    return {
        "original_text": text,
        "translated_text": translated_text,
        "source_language": source_lang,
        "target_language": target_lang,
        "cached": False
    }


def success_response(data):
    """Returns a successful JSON response."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }


def error_response(message):
    """Returns an error JSON response."""
    return {
        "statusCode": 500,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": message})
    }
