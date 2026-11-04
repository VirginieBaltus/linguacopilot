import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def load_module(name, relative_path):
    """Loads a Lambda file as a module. Both Lambdas are named lambda_function.py,
    so they are loaded under distinct names."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def ingest(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("BUCKET_NAME", "test-bucket")
    monkeypatch.setenv("DEEPL_API_KEY", "test-deepl-key")
    monkeypatch.setenv("API_KEY", "secret-key")
    return load_module("lambda_ingest", "aws/lambda_ingest/lambda_function.py")


@pytest.fixture
def sync(monkeypatch):
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-north-1")
    monkeypatch.setenv("DATABRICKS_HOST", "https://example.cloud.databricks.com/")
    monkeypatch.setenv("DATABRICKS_TOKEN", "dapi-test")
    return load_module("lambda_sync", "aws/lambda_sync_databricks/lambda_function.py")