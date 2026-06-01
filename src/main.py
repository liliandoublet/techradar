from src.scrapers import fetch_all_articles
from src.agent.summarizer import summarize_and_score
from src.agent.filter import filter_and_rank
from src.email.digest import send_digest
from src.cache import load_seen, save_seen

def run():
    print("🚀 PulseAI starting...\n")

    # Step 1 — Charger le cache
    print("💾 Step 1 — Loading cache from S3...")
    seen_urls = load_seen()

    # Step 2 — Scrape
    print("\n📡 Step 2 — Fetching articles...")
    all_articles = fetch_all_articles()

    # Step 3 — Filtrer les déjà vus
    new_articles = [a for a in all_articles if a["url"] not in seen_urls]
    print(f"✅ {len(new_articles)} new articles (filtered {len(all_articles) - len(new_articles)} duplicates)")

    # Step 4 — Summarize with Gemini
    print("\n🤖 Step 3 — Summarizing with Gemini...")
    scored = []
    for i, article in enumerate(new_articles[:10]):
        print(f"  Processing {i+1}/20: {article['title'][:30]}...")
        result = summarize_and_score(article)
        scored.append(result)

    # Step 5 — Filter top 10
    print("\n🏆 Step 4 — Filtering top articles...")
    top = filter_and_rank(scored)

    # Step 6 — Send email
    print("\n📧 Step 5 — Sending digest...")
    send_digest(top)

    # Step 7 — Sauvegarder le cache
    print("\n💾 Step 6 — Saving cache to S3...")
    seen_urls.update(a["url"] for a in all_articles)
    save_seen(seen_urls)

    print("\n✅ TechRadar done!")


if __name__ == "__main__":
    run()