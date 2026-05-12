import sendgrid
from sendgrid.helpers.mail import Mail
from src.config import SENDGRID_API_KEY, DIGEST_RECIPIENT, SENDER_EMAIL

def build_html(articles: list[dict]) -> str:

    rows = ""
    for i, a in enumerate(articles, 1):
        bullets_html = "".join(f"<li>{b}</li>" for b in a.get("bullets", []))
        rows += f"""
        <div style="margin-bottom:32px; border-left:4px solid #4F46E5; padding-left:16px;">
            <p style="color:#6B7280; font-size:12px; margin:0">#{i} - {a['source'].upper()} · Score: {a['score']}/10</p>
            <h2 style="margin:4px 0">
                <a href="{a['url']}" style="color:#111827; text-decoration:none">{a['title']}</a>
            </h2>
            <ul style="color:#374151; margin:8px 0; padding-left:20px">
                {bullets_html}
            </ul>
        </div>
        """
    
    return f"""
    <html>
    <body style="font-family:sans-serif; max-width:680px; margin:auto; padding:32px; color:#111827">
        <h1 style="color:#4F46E5">⚡ PulseAI — Daily Tech Digest</h1>
        <p style="color:#6B7280">Your top {len(articles)} articles today, ranked by relevance.</p>
        <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0">
        {rows}
        <hr style="border:none; border-top:1px solid #E5E7EB; margin:24px 0">
        <p style="color:#9CA3AF; font-size:12px">Powered by PulseAI · Gemini AI · Built with ❤️</p>
    </body>
    </html>
    """

def send_digest(articles: list[dict]) -> None:

    html = build_html(articles)

    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=DIGEST_RECIPIENT,
        subject="TechRadar - Your Daily Tech Digest",
        html_content=html
    )

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent! Status: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Email failed: {e}")