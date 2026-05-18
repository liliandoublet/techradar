from src.main import run

def handler(event, context):
    """AWS Lambda entry point."""
    run()
    return {
        "statusCode": 200,
        "body": "TechRadar digest sent successfully!"
    }