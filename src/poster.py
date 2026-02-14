"""
Multi-Platform Poster
Posts generated content to Reddit, Twitter/X, and WordPress.
"""

import os
import praw
import tweepy

# ============================================================
# Reddit Poster
# ============================================================

def get_reddit_client():
    """Initialize Reddit API client"""
    try:
        reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent="AmazonMarketing/1.0",
        )
        return reddit
    except Exception as e:
        print(f"[ERROR] Reddit client init failed: {e}")
        return None


def post_to_reddit(content, subreddits=None):
    """Post content to specified subreddits"""
    if not subreddits:
        subreddits = ["deals", "AmazonDeals", "BuyItForLife"]

    reddit = get_reddit_client()
    if not reddit:
        return []

    results = []
    for sub_name in subreddits:
        try:
            subreddit = reddit.subreddit(sub_name)
            submission = subreddit.submit(
                title=content["reddit_title"],
                selftext=content["post_body"],
            )
            results.append({
                "platform": "reddit",
                "subreddit": sub_name,
                "url": submission.url,
                "status": "success",
            })
            print(f"[POSTED] Reddit r/{sub_name}: {submission.url}")
        except Exception as e:
            results.append({
                "platform": "reddit",
                "subreddit": sub_name,
                "error": str(e),
                "status": "failed",
            })
            print(f"[ERROR] Reddit r/{sub_name}: {e}")

    return results


# ============================================================
# Twitter/X Poster
# ============================================================

def get_twitter_client():
    """Initialize Twitter API client"""
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET"),
        )
        return client
    except Exception as e:
        print(f"[ERROR] Twitter client init failed: {e}")
        return None


def post_to_twitter(content):
    """Post a tweet"""
    client = get_twitter_client()
    if not client:
        return []

    try:
        response = client.create_tweet(text=content["tweet"])
        result = {
            "platform": "twitter",
            "tweet_id": response.data["id"],
            "status": "success",
        }
        print(f"[POSTED] Twitter: {response.data['id']}")
        return [result]
    except Exception as e:
        print(f"[ERROR] Twitter: {e}")
        return [{"platform": "twitter", "error": str(e), "status": "failed"}]


# ============================================================
# WordPress Blog Poster
# ============================================================

def post_to_wordpress(content, product):
    """Post a blog entry to WordPress"""
    import requests

    wp_url = os.getenv("WORDPRESS_URL")
    wp_user = os.getenv("WORDPRESS_USER")
    wp_password = os.getenv("WORDPRESS_APP_PASSWORD")

    if not all([wp_url, wp_user, wp_password]):
        print("[SKIP] WordPress not configured")
        return []

    try:
        api_url = f"{wp_url}/wp-json/wp/v2/posts"
        post_data = {
            "title": product["title"],
            "content": content["blog"],
            "status": "publish",
        }
        response = requests.post(
            api_url,
            json=post_data,
            auth=(wp_user, wp_password),
            timeout=15,
        )
        response.raise_for_status()

        result = {
            "platform": "wordpress",
            "post_id": response.json().get("id"),
            "url": response.json().get("link"),
            "status": "success",
        }
        print(f"[POSTED] WordPress: {result['url']}")
        return [result]

    except Exception as e:
        print(f"[ERROR] WordPress: {e}")
        return [{"platform": "wordpress", "error": str(e), "status": "failed"}]


# ============================================================
# Master Poster
# ============================================================

def post_to_platforms(content, product):
    """Post content to all configured platforms"""
    results = []

    # Reddit
    if os.getenv("REDDIT_CLIENT_ID"):
        results.extend(post_to_reddit(content))

    # Twitter
    if os.getenv("TWITTER_API_KEY"):
        results.extend(post_to_twitter(content))

    # WordPress
    if os.getenv("WORDPRESS_URL"):
        results.extend(post_to_wordpress(content, product))

    return results
