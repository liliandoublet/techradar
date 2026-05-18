import json
import boto3
from botocore.exceptions import ClientError

S3_BUCKET = "techradar-cache"
S3_KEY = "seen_articles.json"

s3 = boto3.client("s3")

def load_seen() -> set:
    """Charge les articles déjà vus depuis S3."""
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
        data = json.loads(response["Body"].read())
        print(f"✅ Cache loaded: {len(data)} seen articles")
        return set(data)
    except ClientError:
        print("ℹ️ No cache found, starting fresh")
        return set()

def save_seen(urls: set) -> None:
    """Sauvegarde les articles vus dans S3."""
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_KEY,
        Body=json.dumps(list(urls)),
        ContentType="application/json"
    )
    print(f"✅ Cache saved: {len(urls)} articles")