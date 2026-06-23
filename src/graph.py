import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from loguru import logger

from src.cache import load_seen, save_seen
from src.config import GEMINI_API_KEY, MAX_ARTICLES, TOPICS
from src.email.digest import send_digest
from src.scrapers.hackernews import fetch_top_stories
from src.scrapers.rss import fetch_rss_articles
from src.state import TechWatchState


def collect_articles(state: TechWatchState) -> dict:
    logger.info("Debut de la collecte des articles...")

    articles = fetch_top_stories(30) + fetch_rss_articles()

    seen: set[str] = set()
    unique: list[dict] = []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    logger.info(f"Articles collectes: {len(unique)}")

    if not unique:
        logger.warning("Aucun article collecte aujourd'hui")
        return {"raw_articles": [], "error": "no_articles"}

    return {"raw_articles": unique}


def filter_and_deduplicate(state: TechWatchState) -> dict:
    logger.info("Filtrage des articles deja traites...")

    seen_urls = load_seen()
    filtered = [a for a in state["raw_articles"] if a["url"] not in seen_urls]

    logger.info(
        f"Articles apres filtrage cache S3: {len(filtered)}"
        f" (ignores: {len(state['raw_articles']) - len(filtered)})"
    )
    return {"filtered_articles": filtered}


def summarize_with_gemini(state: TechWatchState) -> dict:
    logger.info("Resume des articles avec Gemini...")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=GEMINI_API_KEY)
    summaries: list[dict] = []

    try:
        for i, article in enumerate(state["filtered_articles"][:10]):
            logger.info(f"  Traitement {i + 1}/10: {article['title'][:40]}...")
            time.sleep(10)

            prompt = f"""You are a tech news analyst. Given this article, do 2 things:

1. Summarize it in exactly 3 bullet points (concise, informative)
2. Give a relevance score from 0 to 10 based on these topics: {", ".join(TOPICS)}

Article title: {article["title"]}
Article URL: {article["url"]}

Reply in this exact format:
SCORE: <number>
- <bullet 1>
- <bullet 2>
- <bullet 3>
"""
            response = llm.invoke(prompt)
            text = response.content.strip()

            lines = text.split("\n")
            score = float(lines[0].replace("SCORE:", "").strip())
            bullets = [l.strip() for l in lines[1:] if l.strip().startswith("-")]

            summaries.append({**article, "score": score, "bullets": bullets})

        logger.info(f"Resumes generes: {len(summaries)}")
        return {"summaries": summaries, "error": None}

    except Exception as e:
        logger.error(f"Erreur Gemini: {e}")
        return {
            "summaries": summaries,
            "error": "gemini_error",
            "retry_count": state["retry_count"] + 1,
        }


def retry_gemini(state: TechWatchState) -> dict:
    logger.warning(f"Nouvelle tentative Gemini (tentative {state['retry_count']}/3)...")
    return {"error": None, "summaries": []}


def send_email(state: TechWatchState) -> dict:
    logger.info("Envoi de l'email digest...")

    valid = [a for a in state["summaries"] if a.get("bullets")]
    top = sorted(valid, key=lambda x: x["score"], reverse=True)[:MAX_ARTICLES]

    send_digest(top)

    seen_urls = load_seen()
    seen_urls.update(a["url"] for a in state["raw_articles"])
    save_seen(seen_urls)

    logger.info("Email envoye et cache mis a jour.")
    return {"email_sent": True}


def _route_after_collect(state: TechWatchState) -> str:
    if state["error"] == "no_articles":
        logger.info("Fin du pipeline: aucun article collecte aujourd'hui.")
        return END
    return "filter_and_deduplicate"


def _route_after_summarize(state: TechWatchState) -> str:
    if state["error"] == "gemini_error":
        if state["retry_count"] < 3:
            return "retry_gemini"
        logger.error("Echec apres 3 tentatives Gemini. Arret du pipeline.")
        return END
    return "send_email"


_builder = StateGraph(TechWatchState)

_builder.add_node("collect_articles", collect_articles)
_builder.add_node("filter_and_deduplicate", filter_and_deduplicate)
_builder.add_node("summarize_with_gemini", summarize_with_gemini)
_builder.add_node("retry_gemini", retry_gemini)
_builder.add_node("send_email", send_email)

_builder.add_edge(START, "collect_articles")
_builder.add_conditional_edges("collect_articles", _route_after_collect)
_builder.add_edge("filter_and_deduplicate", "summarize_with_gemini")
_builder.add_conditional_edges("summarize_with_gemini", _route_after_summarize)
_builder.add_edge("retry_gemini", "summarize_with_gemini")
_builder.add_edge("send_email", END)

app = _builder.compile()
