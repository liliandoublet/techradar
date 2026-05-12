from src.config import MAX_ARTICLES

def filter_and_rank(articles: list[dict]) -> list[dict]:
    valid = [a for a in articles if a.get("bullets")]
    ranked = sorted(valid, key=lambda x: x["score"], reverse=True)
    top = ranked[:MAX_ARTICLES]
    print(f"✅ Ranked {len(articles)} articles → kept top {len(top)}")
    return top
