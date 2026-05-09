import google.genai as genai
from src.config import GEMINI_API_KEY, TOPICS

client = genai.Client(api_key=GEMINI_API_KEY)

def summarize_and_score(article: dict) -> dict:

    prompt = f"""

You are a tech news analyst. Given this article , do 2 things:

1. Summarize it in exactly 3 bullet points ( concise, informative)
2. Give a relevance score from 0 to 10 based on these topics: {", ".join(TOPICS)}

Article title: {article["title"]}
Article URL: {article["url"]}

Reply in this exact format:
SCORE: <number>
- <bullet 1>
- <bullet 2>
- <bullet 3>
"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()

        lines = text.split("\n")
        score_line = lines[0].replace("SCORE:", "").strip()
        score = float(score_line)

        bullets = [l.strip() for l in lines[1:] if l.strip().startswith("-")]

        return {
            **article,
            "score" : score,
            "bullets": bullets
        }
    
    except Exception as e:
        print(f"⚠️ Gemini failed for '{article['title']}': {e}")
        return {**article, "score": 0, "bullets": []}
    
if __name__ == "__main__":
    test_article = {
         "title": "Python 3.13 released with major performance improvements",
        "url": "https://python.org",
        "source": "hackernews"
    }       

    result = summarize_and_score(test_article)
    print(f"Score: {result['score']}")
    for b in result["bullets"]:
        print(b)    
