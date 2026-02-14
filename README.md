# Amazon Marketing Automation

Automated Amazon affiliate marketing tool powered by Docker.

## How It Works
1. Add your affiliate links to `links.txt` (one per line)
2. Run `docker-compose up`
3. The tool will:
   - Scrape product details (title, price, images, features)
   - Generate marketing copy using AI
   - Post content to configured platforms (Reddit, blogs, etc.)
   - Track all activity in `logs/`

## Setup
1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your API keys
3. Add links to `links.txt`
4. Run: `docker-compose up --build`

## File Structure
```
Amazon-Marketing/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── links.txt              # Your affiliate links (one per line)
├── .env.example           # Template for API keys
├── src/
│   ├── main.py            # Entry point
│   ├── scraper.py         # Scrapes Amazon product data
│   ├── content_gen.py     # AI-powered content generation
│   ├── poster.py          # Posts to Reddit/blogs/social
│   └── tracker.py         # Tracks posted content
└── logs/                  # Activity logs
```

## Supported Platforms
- Reddit (via PRAW)
- Twitter/X (via API)
- WordPress blogs (via REST API)
- Custom webhooks
