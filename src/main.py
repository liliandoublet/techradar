from src.scrapers import fetch_all_articles
from src.agent.summarizer import summarize_and_score
from src.agent.filter import filter_and_rank
from src.email.digest import send_digest

def run():
    print("🚀 PulseAI starting...\n")

    # Step 1 — Scrape
    print("📡 Step 1 — Fetching articles...")
    articles = fetch_all_articles()

    # Step 2 — Summarize with Gemini
    print("\n🤖 Step 2 — Summarizing with Gemini...")
    scored = []
    for i, article in enumerate(articles[:20]):  # limit to 20 to save quota
        print(f"  Processing {i+1}/20: {article['title'][:50]}...")
        result = summarize_and_score(article)
        scored.append(result)

    # Step 3 — Filter top 10
    print("\n🏆 Step 3 — Filtering top articles...")
    top = filter_and_rank(scored)

    # Step 4 — Send email
    print("\n📧 Step 4 — Sending digest...")
    send_digest(top)

    print("\n✅ Techradar done!")


if __name__ == "__main__":
    run()