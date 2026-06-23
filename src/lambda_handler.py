from datetime import datetime

from src.graph import app


def handler(event, context):
    """AWS Lambda entry point."""
    result = app.invoke({
        "raw_articles": [],
        "filtered_articles": [],
        "summaries": [],
        "email_sent": False,
        "retry_count": 0,
        "error": None,
        "run_date": datetime.utcnow().isoformat(),
    })
    return {
        "statusCode": 200,
        "body": {
            "articles_collected": len(result["raw_articles"]),
            "articles_summarized": len(result["summaries"]),
            "email_sent": result["email_sent"],
        },
    }
