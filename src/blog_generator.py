"""
SEO Blog Content Generator
Generates full SEO-optimized blog articles from Amazon affiliate links.
Outputs ready-to-publish HTML or Markdown files.
"""

import os
import json
import openai
from datetime import datetime
from dotenv import load_dotenv
from scraper import scrape_product

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = "blog_output"


def generate_blog_article(product, affiliate_link):
    """Generate a full SEO-optimized blog article for a product"""
    features_text = "\n".join(f"- {f}" for f in product.get("features", [])[:8])

    prompt = f"""
Write a comprehensive, SEO-optimized blog article reviewing this product:

**Product:** {product['title']}
**Price:** ${product.get('price', 'Check current price')}
**Rating:** {product.get('rating', 'N/A')}
**Key Features:**
{features_text}

**Affiliate Link:** {affiliate_link}

Requirements:
1. Title tag (under 60 chars, keyword-rich)
2. Meta description (under 160 chars)
3. H1 headline
4. Introduction (hook the reader, 100 words)
5. "Key Features & Specs" section with bullet points
6. "Who Is This For?" section (target audiences)
7. "Pros and Cons" section
8. "How It Compares" section (vs 2-3 competitors, be general)
9. "Our Verdict" section with clear recommendation
10. FAQ section (5 common questions with answers)
11. Call-to-action with the affiliate link

Use natural language. Include the affiliate link 3-4 times naturally.
Add relevant keywords throughout for SEO.
Format in Markdown.
Target: 1500-2000 words.
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert tech blogger and SEO specialist. "
                        "Write engaging, detailed product reviews that rank well "
                        "on Google. Be authentic, balanced (mention downsides too), "
                        "and genuinely helpful. Never sound like pure advertising."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=4000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Blog generation failed: {e}")
        return None


def generate_seo_metadata(product):
    """Generate SEO metadata for the article"""
    title = product.get("title", "Product Review")
    slug = title.lower()
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = slug.strip().replace("  ", " ").replace(" ", "-")[:80]

    return {
        "slug": slug,
        "title": title,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "category": "Product Reviews",
        "tags": ["amazon", "review", "tech", "deals"],
    }


def save_blog_article(article_md, metadata, product):
    """Save the generated blog article to disk"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slug = metadata["slug"]
    filename = f"{metadata['date']}-{slug}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Add frontmatter
    frontmatter = f"""---
title: "{metadata['title']}"
date: {metadata['date']}
slug: {slug}
category: {metadata['category']}
tags: {json.dumps(metadata['tags'])}
image: {product.get('image_url', '')}
---

"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter + article_md)

    print(f"[SAVED] Blog article: {filepath}")
    return filepath


def generate_social_snippets(product, affiliate_link):
    """Generate social media snippets to promote the blog post"""
    try:
        prompt = f"""
Generate social media posts to promote a blog article about: {product['title']}
Affiliate link: {affiliate_link}

Create:
1. Twitter/X post (under 280 chars, with hashtags)
2. Instagram caption (engaging, with emojis and hashtags)
3. Pinterest description (keyword-rich, 200 chars max)
4. Facebook post (conversational, 2-3 sentences)

Format each with a clear label.
"""
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You write viral social media posts for tech products.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] Social snippet generation failed: {e}")
        return None


# ============================================================
# Batch Blog Generator
# ============================================================

def process_links_for_blog(links_file="links.txt"):
    """Process all links and generate blog articles"""
    if not os.path.exists(links_file):
        print(f"[ERROR] {links_file} not found.")
        return

    with open(links_file, "r") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[BLOG] Processing {len(links)} links for blog content...")

    results = []
    for link in links:
        print(f"\n[BLOG] Scraping: {link}")
        product = scrape_product(link)

        if not product:
            print(f"[SKIP] Could not scrape: {link}")
            continue

        print(f"[BLOG] Generating article for: {product['title']}")
        article = generate_blog_article(product, link)

        if not article:
            print(f"[SKIP] Could not generate article for: {product['title']}")
            continue

        metadata = generate_seo_metadata(product)
        filepath = save_blog_article(article, metadata, product)

        # Generate social snippets
        snippets = generate_social_snippets(product, link)
        if snippets:
            snippets_path = filepath.replace(".md", "-social.md")
            with open(snippets_path, "w", encoding="utf-8") as f:
                f.write(snippets)
            print(f"[SAVED] Social snippets: {snippets_path}")

        results.append({
            "link": link,
            "product": product["title"],
            "blog_file": filepath,
            "status": "success",
        })

    # Save summary
    summary_path = os.path.join(OUTPUT_DIR, "generation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[COMPLETE] Generated {len(results)} blog articles.")
    print(f"[SUMMARY] Saved to: {summary_path}")
    return results


if __name__ == "__main__":
    process_links_for_blog()
