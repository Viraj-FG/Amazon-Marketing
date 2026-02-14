"""
Activity Tracker
Logs all posting activity and prevents duplicate posts.
"""

import os
import json
from datetime import datetime

LOG_DIR = "logs"
POSTED_FILE = os.path.join(LOG_DIR, "posted.json")
ACTIVITY_LOG = os.path.join(LOG_DIR, "activity.jsonl")


def load_posted():
    """Load set of already-posted links"""
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r") as f:
        data = json.load(f)
    return set(data)


def save_posted(posted_set):
    """Save posted links to disk"""
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(POSTED_FILE, "w") as f:
        json.dump(list(posted_set), f, indent=2)


def log_activity(link, product, content, results):
    """Log a posting activity to the activity log"""
    os.makedirs(LOG_DIR, exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "link": link,
        "product_title": product.get("title", "Unknown"),
        "price": product.get("price"),
        "platforms_posted": len([r for r in results if r.get("status") == "success"]),
        "platforms_failed": len([r for r in results if r.get("status") == "failed"]),
        "results": results,
    }

    with open(ACTIVITY_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Mark link as posted
    posted = load_posted()
    posted.add(link)
    save_posted(posted)

    print(f"[LOGGED] {product.get('title', 'Unknown')} - {len(results)} platform(s)")
