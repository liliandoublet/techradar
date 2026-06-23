from typing import TypedDict


class TechWatchState(TypedDict):
    raw_articles: list[dict]
    filtered_articles: list[dict]
    summaries: list[dict]
    email_sent: bool
    retry_count: int
    error: str | None
    run_date: str
