"""
Amazon Marketing Automation - Main Entry Point
Reads links.txt, scrapes product data, generates content, and posts automatically.
"""

import os
import time
import schedule
from dotenv import load_dotenv
from scraper import scrape_product
from content_gen import generate_content
from poster import post_to_platforms
from tracker import log_activity, load_posted

load_dotenv()

LINKS_FILE = "links.txt"
LOG_DIR = "logs"

def load_links():
    """Load affiliate links from links.txt"""
    if not os.path.exists(LINKS_FILE):
        print(f"[ERROR] {LINKS_FILE} not found. Please add your links.")
        return []

    with open(LINKS_FILE, "r") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[INFO] Loaded {len(links)} links from {LINKS_FILE}")
    return links


def process_link(link):
    """Full pipeline: scrape -> generate content -> post -> log"""
    print(f"\n{'='*60}")
    print(f"[PROCESSING] {link}")
    print(f"{'='*60}")

    # Step 1: Scrape product data
    product = scrape_product(link)
    if not product:
        print(f"[SKIP] Could not scrape: {link}")
        return

    print(f"[SCRAPED] {product['title']} - ${product.get('price', 'N/A')}")

    # Step 2: Generate marketing content
    content = generate_content(product)
    if not content:
        print(f"[SKIP] Could not generate content for: {product['title']}")
        return

    print(f"[GENERATED] Content ready ({len(content['post_body'])} chars)")

    # Step 3: Post to configured platforms
    results = post_to_platforms(content, product)

    # Step 4: Log activity
    log_activity(link, product, content, results)
    print(f"[DONE] {product['title']} posted to {len(results)} platforms")


def run():
    """Main execution loop"""
    os.makedirs(LOG_DIR, exist_ok=True)

    links = load_links()
    if not links:
        return

    posted = load_posted()

    for link in links:
        if link in posted:
            print(f"[SKIP] Already posted: {link}")
            continue
        process_link(link)
        time.sleep(5)  # Rate limiting between posts

    print("\n[COMPLETE] All links processed.")


if __name__ == "__main__":
    run()
