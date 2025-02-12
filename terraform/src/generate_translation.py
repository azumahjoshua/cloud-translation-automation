import json
import boto3
import os
import uuid
import hashlib
from botocore.exceptions import ClientError

# AWS Clients
translate_client = boto3.client("translate")
s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Environment Variables
INPUT_BUCKET = os.environ.get("TRANSLATION_INPUT_BUCKET_NAME")
OUTPUT_BUCKET = os.environ.get("TRANSLATION_OUTPUT_BUCKET_NAME")
CACHE_TABLE_NAME = os.environ.get("TRANSLATION_CACHE_TABLE_NAME")
cache_table = dynamodb.Table(CACHE_TABLE_NAME)

def get_hash_key(text, source_lang, target_lang):
    """Generates a SHA-256 hash key for caching."""
    key_string = f"{source_lang}-{target_lang}-{text}"
    return hashlib.sha256(key_string.encode()).hexdigest()

def get_cached_translation(text, source_lang, target_lang):
    """Checks DynamoDB cache for an existing translation using hash key."""
    try:
        response = cache_table.get_item(Key={"hash": get_hash_key(text, source_lang, target_lang)})
        return response.get("Item", {}).get("translated_text")
    except ClientError as e:
        print(f"Error accessing cache: {e}")
        return None

def store_translation_in_cache(text, source_lang, target_lang, translated_text):
    """Stores new translations in DynamoDB cache using hash key."""
    try:
        cache_table.put_item(
            Item={
                "hash": get_hash_key(text, source_lang, target_lang),  
                "src_locale": source_lang,
                "target_locale": target_lang,
                "src_text": text,
                "translated_text": translated_text
            }
        )
    except ClientError as e:
        print(f"Error writing to cache: {e}")

def translate_text(text, source_lang, target_lang):
    """Translates text using AWS Translate, handling both strings and lists."""
    if isinstance(text, list):
        return [translate_text(sentence, source_lang, target_lang) for sentence in text]

    if not isinstance(text, str) or not text.strip():
        return text

    cached_translation = get_cached_translation(text, source_lang, target_lang)
    if cached_translation:
        return cached_translation

    try:
        response = translate_client.translate_text(
            Text=text, SourceLanguageCode=source_lang, TargetLanguageCode=target_lang
        )
        translated_text = response["TranslatedText"]
        store_translation_in_cache(text, source_lang, target_lang, translated_text)
        return translated_text
    except ClientError as e:
        print(f"Error calling Translate API: {e}")
        return text

def handle_uploaded_file(s3_key):
    """Processes uploaded JSON file from S3, translates content while checking cache, and stores the result."""
    try:
        # Fetch file from S3
        response = s3_client.get_object(Bucket=INPUT_BUCKET, Key=s3_key)
        file_content = json.loads(response["Body"].read().decode("utf-8"))

        source_lang = file_content.get("source_language", "auto")
        target_lang = file_content.get("target_language", "en")
        text_data = file_content.get("text", [])

        if isinstance(text_data, str):
            text_data = [text_data]  # Convert single string to list

        translated_sentences = []
        uncached_sentences = []

        # Check cache for each sentence
        for sentence in text_data:
            cached_translation = get_cached_translation(sentence, source_lang, target_lang)
            if cached_translation:
                translated_sentences.append(cached_translation)
            else:
                uncached_sentences.append(sentence)

        # Translate only uncached sentences
        if uncached_sentences:
            new_translations = translate_text(uncached_sentences, source_lang, target_lang)
            translated_sentences.extend(new_translations)

            # Store new translations in cache
            for original, translated in zip(uncached_sentences, new_translations):
                store_translation_in_cache(original, source_lang, target_lang, translated)

        translated_data = {
            "original_text": text_data,
            "translated_text": translated_sentences,
            "source_language": source_lang,
            "target_language": target_lang
        }

        # Store translated JSON in S3
        translated_file_key = f"translations/{s3_key.split('/')[-1]}"
        s3_client.put_object(Bucket=OUTPUT_BUCKET, Key=translated_file_key, Body=json.dumps(translated_data))

        return {"message": "File translated successfully", "s3_key": translated_file_key}

    except ClientError as e:
        return {"error": str(e)}
