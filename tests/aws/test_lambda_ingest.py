import json
from unittest.mock import MagicMock

VALID_CLICK = {
    "word": "Miete",
    "sentence": "Wie zahle ich die Miete?",
    "video_id": "abc123",
    "timestamp_sec": 3.2,
}


def api_event(payload, key="secret-key"):
    """Builds an event as sent by API Gateway."""
    headers = {"x-api-key": key} if key is not None else {}
    return {"requestContext": {}, "headers": headers, "body": json.dumps(payload)}


def mock_s3(ingest, monkeypatch):
    s3 = MagicMock()
    monkeypatch.setattr(ingest, "s3", s3)
    return s3


def test_rejects_request_without_key(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)
    response = ingest.lambda_handler(api_event(VALID_CLICK, key=None), None)
    assert response["statusCode"] == 401
    s3.put_object.assert_not_called()


def test_rejects_request_with_wrong_key(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)
    response = ingest.lambda_handler(api_event(VALID_CLICK, key="wrong-key"), None)
    assert response["statusCode"] == 401
    s3.put_object.assert_not_called()


def test_rejects_click_with_missing_fields(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)
    incomplete = {"word": "Miete", "video_id": "abc123"}
    response = ingest.lambda_handler(api_event(incomplete), None)
    assert response["statusCode"] == 400
    s3.put_object.assert_not_called()


def test_saves_click_with_translations(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)
    monkeypatch.setattr(ingest, "translate", lambda word, sentence: ("loyer", "Comment payer le loyer ?"))

    response = ingest.lambda_handler(api_event(VALID_CLICK), None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["translation"] == "loyer"

    saved = s3.put_object.call_args.kwargs
    assert saved["Bucket"] == "test-bucket"
    assert saved["Key"].startswith("events/date=")
    assert saved["Key"].endswith(".json")
    record = json.loads(saved["Body"].decode("utf-8"))
    assert record["word"] == "Miete"
    assert record["word_translation"] == "loyer"
    assert record["event_id"] == body["event_id"]


def test_saves_click_even_when_deepl_fails(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)

    def failing_urlopen(*args, **kwargs):
        raise ingest.urllib.error.URLError("DeepL unavailable")

    monkeypatch.setattr(ingest.urllib.request, "urlopen", failing_urlopen)

    response = ingest.lambda_handler(api_event(VALID_CLICK), None)

    assert response["statusCode"] == 200
    record = json.loads(s3.put_object.call_args.kwargs["Body"].decode("utf-8"))
    assert record["word"] == "Miete"
    assert record["word_translation"] is None


def test_console_invocation_does_not_need_key(ingest, monkeypatch):
    mock_s3(ingest, monkeypatch)
    monkeypatch.setattr(ingest, "translate", lambda word, sentence: ("loyer", "traduction"))
    response = ingest.lambda_handler(VALID_CLICK, None)
    assert response["statusCode"] == 200

def test_translate_route_does_not_save(ingest, monkeypatch):
    s3 = mock_s3(ingest, monkeypatch)
    monkeypatch.setattr(ingest, "translate", lambda word, sentence: ("loyer", "Comment payer le loyer ?"))
    event = api_event({"word": "Miete", "sentence": "Wie zahle ich die Miete?"})
    event["routeKey"] = "POST /translate"

    response = ingest.lambda_handler(event, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["translation"] == "loyer"
    s3.put_object.assert_not_called()