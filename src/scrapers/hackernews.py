import httpx

HN_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{}.json"

def fetch_top_stories(limit: int = 30) -> list[dict]:
    response = httpx.get(HN_TOP_STORIES_URL, timeout=10)
    story_ids = response.json()[:limit]

    articles = []
    for story_id in story_ids:
        try:
            item = httpx.get(HN_ITEM_URL.format(story_id), timeout=10).json()

            if item.get("url"):
                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "score": item.get("score", 0),
                    "source": "hackernews"
                })
        except Exception as e:
            print(f"⚠️ Skipping story {story_id}: {e}")
            continue

    return articles

if __name__ == "__main__":
    articles = fetch_top_stories(10)
    for a in articles:
        print(f"[{a['score']}] {a['title']}")
        print(f"  → {a['url']}\n")