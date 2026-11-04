import os
import urllib.error
import urllib.parse
import urllib.request

import boto3

s3 = boto3.client("s3")
DATABRICKS_HOST = os.environ["DATABRICKS_HOST"].rstrip("/")
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]
VOLUME_PATH = os.environ.get("VOLUME_PATH", "/Volumes/workspace/linguacopilot/raw_events")


def upload_to_volume(key, content):
    """Uploads a file to the Databricks volume, keeping the same folder structure as S3."""
    target_path = urllib.parse.quote(f"{VOLUME_PATH}/{key}", safe="/=")
    url = f"{DATABRICKS_HOST}/api/2.0/fs/files{target_path}?overwrite=true"
    request = urllib.request.Request(
        url,
        data=content,
        method="PUT",
        headers={
            "Authorization": f"Bearer {DATABRICKS_TOKEN}",
            "Content-Type": "application/octet-stream",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return response.status
    except urllib.error.HTTPError as error:
        print(f"Databricks upload failed (HTTP {error.code}): {error.read().decode()}")
        raise


def lambda_handler(event, context):
    # S3 sends one record per new file
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        content = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        status = upload_to_volume(key, content)
        print(f"Uploaded {key} to Databricks volume (HTTP {status})")

    return {"uploaded": len(event["Records"])}