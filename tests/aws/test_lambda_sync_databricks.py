from unittest.mock import MagicMock


def s3_event(key):
    """Builds an event as sent by S3 when a new file is created."""
    return {"Records": [{"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": key}}}]}


def mock_s3(sync, monkeypatch, content):
    s3 = MagicMock()
    s3.get_object.return_value = {"Body": MagicMock(read=lambda: content)}
    monkeypatch.setattr(sync, "s3", s3)
    return s3


def test_uploads_file_with_same_path(sync, monkeypatch):
    mock_s3(sync, monkeypatch, b'{"word": "Miete"}')
    uploads = []
    monkeypatch.setattr(sync, "upload_to_volume", lambda key, content: uploads.append((key, content)) or 204)

    result = sync.lambda_handler(s3_event("events/date=2026-11-04/abc.json"), None)

    assert result == {"uploaded": 1}
    assert uploads == [("events/date=2026-11-04/abc.json", b'{"word": "Miete"}')]


def test_decodes_url_encoded_s3_keys(sync, monkeypatch):
    s3 = mock_s3(sync, monkeypatch, b"{}")
    uploads = []
    monkeypatch.setattr(sync, "upload_to_volume", lambda key, content: uploads.append(key) or 204)

    sync.lambda_handler(s3_event("events/date%3D2026-11-04/abc.json"), None)

    s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="events/date=2026-11-04/abc.json")
    assert uploads == ["events/date=2026-11-04/abc.json"]


def test_builds_databricks_request(sync, monkeypatch):
    captured = {}

    class FakeResponse:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured["request"] = request
        return FakeResponse()

    monkeypatch.setattr(sync.urllib.request, "urlopen", fake_urlopen)

    status = sync.upload_to_volume("events/date=2026-11-04/abc.json", b"{}")

    request = captured["request"]
    assert status == 204
    assert request.get_method() == "PUT"
    assert request.full_url == (
        "https://example.cloud.databricks.com/api/2.0/fs/files"
        "/Volumes/workspace/linguacopilot/raw_events/events/date=2026-11-04/abc.json?overwrite=true"
    )
    assert request.get_header("Authorization") == "Bearer dapi-test"