from unittest.mock import MagicMock, patch

from src.graph import app

ARTICLES = [{"title": "Test Article", "url": "https://example.com/test", "score": 5, "source": "test"}]

INITIAL_STATE = {
    "raw_articles": [],
    "filtered_articles": [],
    "summaries": [],
    "email_sent": False,
    "retry_count": 0,
    "error": None,
    "run_date": "2026-06-23T00:00:00",
}

SUCCESS_RESPONSE = "SCORE: 8\n- Bullet point one\n- Bullet point two\n- Bullet point three"


def test_gemini_fails_twice_then_succeeds():
    """Gemini raises on attempts 1 and 2, succeeds on attempt 3.
    Expected: retry_count == 2, email_sent == True.
    """
    invoke_side_effects = [
        Exception("Gemini rate limit"),
        Exception("Gemini unavailable"),
        MagicMock(content=SUCCESS_RESPONSE),
    ]

    mock_invoke = MagicMock(side_effect=invoke_side_effects)

    with (
        patch("src.graph.fetch_top_stories", return_value=ARTICLES),
        patch("src.graph.fetch_rss_articles", return_value=[]),
        patch("src.graph.load_seen", return_value=set()),
        patch("src.graph.save_seen"),
        patch("src.graph.send_digest"),
        patch("src.graph.time.sleep"),
        patch("src.graph.ChatGoogleGenerativeAI") as MockLLM,
    ):
        MockLLM.return_value.invoke = mock_invoke
        result = app.invoke(INITIAL_STATE)

    assert result["retry_count"] == 2
    assert result["email_sent"] is True
    assert len(result["summaries"]) == 1
    assert result["summaries"][0]["score"] == 8.0


def test_gemini_fails_three_times_ends_without_email():
    """Gemini exhausts all 3 retries. Expected: email_sent == False, retry_count == 3."""
    mock_invoke = MagicMock(side_effect=Exception("Persistent Gemini error"))

    with (
        patch("src.graph.fetch_top_stories", return_value=ARTICLES),
        patch("src.graph.fetch_rss_articles", return_value=[]),
        patch("src.graph.load_seen", return_value=set()),
        patch("src.graph.save_seen"),
        patch("src.graph.time.sleep"),
        patch("src.graph.ChatGoogleGenerativeAI") as MockLLM,
    ):
        MockLLM.return_value.invoke = mock_invoke
        result = app.invoke(INITIAL_STATE)

    assert result["retry_count"] == 3
    assert result["email_sent"] is False
