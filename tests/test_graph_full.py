from unittest.mock import MagicMock, patch

from src.graph import app

HN_ARTICLES = [
    {"title": "LLM Agents in Production", "url": "https://hn.com/1", "score": 120, "source": "hackernews"},
    {"title": "Python 3.14 Released", "url": "https://hn.com/2", "score": 95, "source": "hackernews"},
]
RSS_ARTICLES = [
    {"title": "Cloud Cost Optimization Tips", "url": "https://rss.com/3", "score": 0, "source": "PythonInsider"},
]

GEMINI_RESPONSES = [
    "SCORE: 9\n- LLMs now run in prod environments\n- Latency is the main challenge\n- New tooling simplifies deployment",
    "SCORE: 7\n- Python 3.14 ships faster CPython\n- New typing improvements land\n- Deprecation of legacy features",
    "SCORE: 6\n- Reserved instances cut costs by 40%\n- Spot instances suit batch workloads\n- Tagging strategy is essential",
]

INITIAL_STATE = {
    "raw_articles": [],
    "filtered_articles": [],
    "summaries": [],
    "email_sent": False,
    "retry_count": 0,
    "error": None,
    "run_date": "2026-06-23T00:00:00",
}


def test_full_pipeline_happy_path():
    """End-to-end run with mocked scrapers, Gemini, S3 and SendGrid.
    Verifies articles flow through all nodes and an email is sent.
    """
    gemini_iter = iter(GEMINI_RESPONSES)

    def mock_invoke(_prompt):
        return MagicMock(content=next(gemini_iter))

    with (
        patch("src.graph.fetch_top_stories", return_value=HN_ARTICLES),
        patch("src.graph.fetch_rss_articles", return_value=RSS_ARTICLES),
        patch("src.graph.load_seen", return_value=set()),
        patch("src.graph.save_seen") as mock_save,
        patch("src.graph.send_digest") as mock_send,
        patch("src.graph.time.sleep"),
        patch("src.graph.ChatGoogleGenerativeAI") as MockLLM,
    ):
        MockLLM.return_value.invoke = mock_invoke
        result = app.invoke(INITIAL_STATE)

    assert result["email_sent"] is True
    assert result["error"] is None
    assert result["retry_count"] == 0
    assert len(result["raw_articles"]) == 3
    assert len(result["filtered_articles"]) == 3
    assert len(result["summaries"]) == 3

    summaries_by_score = sorted(result["summaries"], key=lambda x: x["score"], reverse=True)
    assert summaries_by_score[0]["score"] == 9.0

    mock_send.assert_called_once()
    mock_save.assert_called_once()


def test_full_pipeline_deduplicates_against_cache():
    """Articles already in the S3 cache are excluded from summarization."""
    cached_urls = {"https://hn.com/1", "https://hn.com/2"}

    gemini_iter = iter(GEMINI_RESPONSES)

    def mock_invoke(_prompt):
        return MagicMock(content=next(gemini_iter))

    with (
        patch("src.graph.fetch_top_stories", return_value=HN_ARTICLES),
        patch("src.graph.fetch_rss_articles", return_value=RSS_ARTICLES),
        patch("src.graph.load_seen", return_value=cached_urls),
        patch("src.graph.save_seen"),
        patch("src.graph.send_digest"),
        patch("src.graph.time.sleep"),
        patch("src.graph.ChatGoogleGenerativeAI") as MockLLM,
    ):
        MockLLM.return_value.invoke = mock_invoke
        result = app.invoke(INITIAL_STATE)

    assert len(result["raw_articles"]) == 3
    assert len(result["filtered_articles"]) == 1
    assert result["filtered_articles"][0]["url"] == "https://rss.com/3"
    assert len(result["summaries"]) == 1
    assert result["email_sent"] is True


def test_full_pipeline_preserves_run_date():
    with (
        patch("src.graph.fetch_top_stories", return_value=[]),
        patch("src.graph.fetch_rss_articles", return_value=[]),
    ):
        result = app.invoke({**INITIAL_STATE, "run_date": "2026-06-23T08:00:00"})

    assert result["run_date"] == "2026-06-23T08:00:00"
