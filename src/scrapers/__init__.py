from .hackernews import fetch_top_stories
from .rss import fetch_rss_articles

def fetch_all_articles() -> list[dict]:

    articles = []
    articles += fetch_top_stories(30)
    articles += fetch_rss_articles()

    seen = set()
    unique = []
    for a in articles:
        if a ["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)

    print(f"✅ Fetched {len(unique)} unique articles")
    return unique