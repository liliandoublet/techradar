Project to monitor new articles on Reddit about machine learning, agentic AI, and various technologies. Provides a summary of articles in a few bullet points, along with links to the top 10 articles each day. Learning how to use AWS and the ClaudeCode AI agent.

Phase 1 - Data Collection

Each run, the scraper layer fetches raw articles form all configured sources in parallel. Article IDs are checked against the S3 cache; duplicate are discard immediately.

Phase 2 - AI Processing

New articles are batched and sent to Claude. For each article, Claude retruns a structured summary and a relevance score agains the configured topics

Phase 3 - Ranking & Selection

Articles are sorted by relevance score. The top article are selected for the digest.

Phase 4 - Delivery

A clean HTML email is generated and sent via SendDrid. All processed article IDs are written back to the S3 cache to prevent future duplicates.

Phase 5 - Scheduling

AWS EventBridge triggers the Lambda function on a daily cron shedule at 8 a.m Paris time.