from unittest.mock import patch

from src.graph import app

INITIAL_STATE = {
    "raw_articles": [],
    "filtered_articles": [],
    "summaries": [],
    "email_sent": False,
    "retry_count": 0,
    "error": None,
    "run_date": "2026-06-23T00:00:00",
}


def test_no_articles_ends_without_email():
    with (
        patch("src.graph.fetch_top_stories", return_value=[]),
        patch("src.graph.fetch_rss_articles", return_value=[]),
    ):
        result = app.invoke(INITIAL_STATE)

    assert result["error"] == "no_articles"
    assert result["email_sent"] is False
    assert result["raw_articles"] == []
    assert result["summaries"] == []


def test_no_articles_skips_filter_and_gemini():
    """Verify filter and Gemini nodes are never reached when collect returns nothing."""
    with (
        patch("src.graph.fetch_top_stories", return_value=[]),
        patch("src.graph.fetch_rss_articles", return_value=[]),
        patch("src.graph.load_seen") as mock_load,
        patch("src.graph.ChatGoogleGenerativeAI") as mock_llm,
    ):
        app.invoke(INITIAL_STATE)

    mock_load.assert_not_called()
    mock_llm.assert_not_called()
