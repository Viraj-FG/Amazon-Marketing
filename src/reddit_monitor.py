"""
Reddit Alert Monitor
Scans subreddits for keywords related to your products.
Sends WhatsApp notifications with pre-written replies when matches are found.
"""

import os
import time
import json
import praw
import requests
from datetime import datetime
from dotenv import load_dotenv
from content_gen import generate_content
from scraper import scrape_product

load_dotenv()

# ============================================================
# Configuration
# ============================================================

WATCH_CONFIG_FILE = "watch_config.json"
ALERTS_LOG = "logs/alerts.jsonl"
SEEN_FILE = "logs/seen_posts.json"

# Default subreddits to monitor
DEFAULT_SUBREDDITS = [
    "macmini", "mac", "apple", "SuggestALaptop", "laptops",
    "MiniPCs", "BuildAPC", "techsupport", "Frugal",
    "BuyItForLife", "deals", "AmazonDeals"
]

# Default keywords to watch for
DEFAULT_KEYWORDS = [
    "mac mini", "which laptop", "laptop recommendation",
    "should I buy", "best desktop", "mini pc",
    "computer recommendation", "upgrade from",
    "looking for a computer", "need a new computer",
    "worth buying", "best value"
]

POLL_INTERVAL_SECONDS = 300  # Check every 5 minutes


# ============================================================
# Watch Config Management
# ============================================================

def load_watch_config():
    """Load watch configuration (products, keywords, subreddits)"""
    if os.path.exists(WATCH_CONFIG_FILE):
        with open(WATCH_CONFIG_FILE, "r") as f:
            return json.load(f)

    # Default config
    config = {
        "products": [],
        "subreddits": DEFAULT_SUBREDDITS,
        "keywords": DEFAULT_KEYWORDS,
        "webhook_url": os.getenv("WEBHOOK_URL", ""),
        "whatsapp_notify": True,
    }
    save_watch_config(config)
    return config


def save_watch_config(config):
    """Save watch configuration"""
    with open(WATCH_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def add_product_to_watch(link, keywords=None):
    """Add a product link to monitor with optional custom keywords"""
    config = load_watch_config()
    product_entry = {
        "link": link,
        "keywords": keywords or [],
        "added_at": datetime.utcnow().isoformat(),
    }
    config["products"].append(product_entry)
    save_watch_config(config)
    print(f"[WATCH] Added product: {link}")


# ============================================================
# Seen Posts Tracking
# ============================================================

def load_seen():
    """Load set of already-seen post IDs"""
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen(seen_set):
    """Save seen post IDs"""
    os.makedirs("logs", exist_ok=True)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_set), f)


# ============================================================
# Reddit Scanner
# ============================================================

def get_reddit_client():
    """Initialize Reddit API client"""
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent="AmazonMarketingMonitor/1.0",
    )


def scan_subreddits(reddit, config):
    """Scan configured subreddits for keyword matches"""
    seen = load_seen()
    matches = []

    for sub_name in config["subreddits"]:
        try:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.new(limit=25):
                if post.id in seen:
                    continue

                # Check title and body against keywords
                text = f"{post.title} {post.selftext}".lower()
                matched_keywords = [
                    kw for kw in config["keywords"]
                    if kw.lower() in text
                ]

                if matched_keywords:
                    match = {
                        "post_id": post.id,
                        "subreddit": sub_name,
                        "title": post.title,
                        "body": post.selftext[:500],
                        "url": f"https://reddit.com{post.permalink}",
                        "author": str(post.author),
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "matched_keywords": matched_keywords,
                        "created_utc": datetime.utcfromtimestamp(post.created_utc).isoformat(),
                        "found_at": datetime.utcnow().isoformat(),
                    }
                    matches.append(match)

                seen.add(post.id)

        except Exception as e:
            print(f"[ERROR] Scanning r/{sub_name}: {e}")

    save_seen(seen)
    return matches


# ============================================================
# Reply Generator
# ============================================================

def generate_reply(match, product_link):
    """Generate a natural, helpful reply for a matched post"""
    prompt_context = f"""
Someone on Reddit (r/{match['subreddit']}) posted:

Title: {match['title']}
Body: {match['body']}

They matched keywords: {', '.join(match['matched_keywords'])}

Write a helpful, genuine reply that naturally recommends the product.
Include this affiliate link naturally: {product_link}
Keep it conversational and authentic — NOT spammy.
Max 200 words.
"""
    try:
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write helpful Reddit comments. Be genuine, "
                        "conversational, and provide real value. Never sound "
                        "like an ad or spam. Include personal experience tone."
                    ),
                },
                {"role": "user", "content": prompt_context},
            ],
            max_tokens=300,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Reply generation failed: {e}")
        return None


# ============================================================
# Notification System
# ============================================================

def send_notification(match, suggested_reply):
    """Send alert notification (webhook or console)"""
    alert = {
        "type": "reddit_alert",
        "subreddit": match["subreddit"],
        "title": match["title"],
        "url": match["url"],
        "keywords": match["matched_keywords"],
        "suggested_reply": suggested_reply,
        "timestamp": datetime.utcnow().isoformat(),
    }

    # Log alert
    os.makedirs("logs", exist_ok=True)
    with open(ALERTS_LOG, "a") as f:
        f.write(json.dumps(alert) + "\n")

    # Console output
    print(f"\n{'='*60}")
    print(f"🚨 ALERT: Match in r/{match['subreddit']}")
    print(f"📌 Title: {match['title']}")
    print(f"🔗 URL: {match['url']}")
    print(f"🔑 Keywords: {', '.join(match['matched_keywords'])}")
    print(f"\n💬 Suggested Reply:")
    print(suggested_reply)
    print(f"{'='*60}\n")

    # Webhook notification (if configured)
    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        try:
            requests.post(webhook_url, json=alert, timeout=10)
        except Exception as e:
            print(f"[ERROR] Webhook failed: {e}")

    return alert


# ============================================================
# Main Monitor Loop
# ============================================================

def run_monitor():
    """Main monitoring loop"""
    print("[MONITOR] Reddit Alert Monitor starting...")

    config = load_watch_config()
    reddit = get_reddit_client()

    # Get the first product link for replies
    product_link = None
    if config["products"]:
        product_link = config["products"][0]["link"]

    print(f"[MONITOR] Watching {len(config['subreddits'])} subreddits")
    print(f"[MONITOR] Tracking {len(config['keywords'])} keywords")
    print(f"[MONITOR] Product link: {product_link or 'None configured'}")
    print(f"[MONITOR] Poll interval: {POLL_INTERVAL_SECONDS}s\n")

    while True:
        try:
            matches = scan_subreddits(reddit, config)

            if matches:
                print(f"[MONITOR] Found {len(matches)} new matches!")
                for match in matches:
                    reply = None
                    if product_link:
                        reply = generate_reply(match, product_link)
                    send_notification(match, reply)
            else:
                print(f"[MONITOR] No new matches. Sleeping {POLL_INTERVAL_SECONDS}s...")

            time.sleep(POLL_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n[MONITOR] Shutting down.")
            break
        except Exception as e:
            print(f"[ERROR] Monitor error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    run_monitor()
