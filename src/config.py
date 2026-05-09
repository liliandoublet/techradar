import os
from dotenv import load_dotenv

load_dotenv()

# AI
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

#Email
SENDGRID_API_API = os.getenv("SENDGRID_API_KPI")
DIGEST_RECIPIENT = os.getenv("DIGEST_RECIPIENT")

# Agent
TOPICS = os.getenv("TOPICS", "AI,Python,Cloud").split(",")
MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", 10))

# AWS
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "pulseai-cache")