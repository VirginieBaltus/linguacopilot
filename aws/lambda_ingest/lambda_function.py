import hmac
import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

import boto3

s3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_NAME"]
DEEPL_API_KEY = os.environ["DEEPL_API_KEY"]
API_KEY = os.environ["API_KEY"]
DEEPL_URL = "https://api-free.deepl.com/v2/translate"
SOURCE_LANG = os.environ.get("SOURCE_LANG", "DE")
TARGET_LANG = os.environ.get("TARGET_LANG", "FR")
REQUIRED_FIELDS = ["word", "sentence", "video_id"]


def is_authorized(event):
    """Requests coming through API Gateway must carry the right key.
    Direct invocations (console tests) already require AWS permissions."""
    if "requestContext" not in event:
        return True
    provided_key = (event.get("headers") or {}).get("x-api-key", "")
    return hmac.compare_digest(provided_key, API_KEY)


def translate(word, sentence):
    """Translates the word (using the sentence as context) and the sentence.
    Returns (None, None) if DeepL fails, so the click is still saved."""
    body = json.dumps(
        {
            "text": [word, sentence],
            "source_lang": SOURCE_LANG,
            "target_lang": TARGET_LANG,
            "context": sentence,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        DEEPL_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": f"DeepL-Auth-Key {DEEPL_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            translations = json.loads(response.read())["translations"]
        return translations[0]["text"], translations[1]["text"]
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, ValueError) as error:
        print(f"DeepL translation failed: {error}")
        return None, None


def json_response(status_code, body):
    return {"statusCode": status_code, "body": json.dumps(body, ensure_ascii=False)}


def lambda_handler(event, context):
    if not is_authorized(event):
        return json_response(401, {"error": "Unauthorized"})

    # From API Gateway the payload is in "body", from a console test it is the event itself
    body = event.get("body")
    payload = json.loads(body) if body else event

    # Hover translation: translate only, nothing is saved
    if event.get("routeKey") == "POST /translate":
        if not payload.get("word") or not payload.get("sentence"):
            return json_response(400, {"error": "Missing word or sentence"})
        word_translation, sentence_translation = translate(payload["word"], payload["sentence"])
        if word_translation is None:
            return json_response(502, {"error": "Translation unavailable"})
        return json_response(200, {"translation": word_translation, "sentence_translation": sentence_translation})

    # Click: translate and save the event for the flashcards
    missing = [field for field in REQUIRED_FIELDS if not payload.get(field)]
    if missing:
        return json_response(400, {"error": f"Missing fields: {missing}"})

    word_translation, sentence_translation = translate(payload["word"], payload["sentence"])

    now = datetime.now(timezone.utc)
    event_id = str(uuid.uuid4())
    record = {
        **payload,
        "word_translation": word_translation,
        "sentence_translation": sentence_translation,
        "source_lang": SOURCE_LANG,
        "target_lang": TARGET_LANG,
        "event_id": event_id,
        "ingested_at": now.isoformat(),
    }

    key = f"events/date={now:%Y-%m-%d}/{event_id}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(record, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
    )

    return json_response(
        200,
        {"event_id": event_id, "translation": word_translation, "sentence_translation": sentence_translation},
    )