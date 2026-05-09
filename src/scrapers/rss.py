import feedparser

RSS_FEEDS = [
    "https://feeds.feedburner.com/PythonInsider",
    "https://news.ycombinator.com/rss",
    "https://www.reddit.com/r/MachineLearning/.rss",
]

def fetch_rss_articles(feeds: list[str] = RSS_FEEDS) -> list[dict]:

    articles = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:
            articles.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "score": 0, 
                "source": feed.feed.get("title", "rss")
            })

    return articles


if __name__ == "__main__":
    articles = fetch_rss_articles()
    for a in articles:
        print(f"[{a['source']}] {a['title']}")
        print(f"  → {a['url']}\n")