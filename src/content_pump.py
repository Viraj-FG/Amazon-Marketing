"""
Content Pump - High Volume Content Generator
Generates maximum content across all platforms from affiliate links.
Produces: blog articles, social posts, comparison articles, deal roundups,
buyer's guides, and newsletter content.
"""

import os
import json
import openai
from datetime import datetime
from dotenv import load_dotenv
from scraper import scrape_product

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

OUTPUT_DIR = "content_output"


def generate_all_content(product, affiliate_link):
    """Generate every type of content for a single product"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    slug = slugify(product["title"])
    product_dir = os.path.join(OUTPUT_DIR, slug)
    os.makedirs(product_dir, exist_ok=True)

    print(f"\n[PUMP] Generating all content for: {product['title']}")

    results = {}

    # 1. Full Blog Review (1500-2000 words)
    results["blog_review"] = generate_and_save(
        product, affiliate_link, product_dir,
        "blog_review.md", generate_blog_review
    )

    # 2. Short Blog Post (500 words)
    results["short_post"] = generate_and_save(
        product, affiliate_link, product_dir,
        "short_post.md", generate_short_post
    )

    # 3. Comparison Article (vs competitors)
    results["comparison"] = generate_and_save(
        product, affiliate_link, product_dir,
        "comparison_article.md", generate_comparison
    )

    # 4. Buyer's Guide
    results["buyers_guide"] = generate_and_save(
        product, affiliate_link, product_dir,
        "buyers_guide.md", generate_buyers_guide
    )

    # 5. Top 10 Reasons Article
    results["top_reasons"] = generate_and_save(
        product, affiliate_link, product_dir,
        "top_10_reasons.md", generate_top_reasons
    )

    # 6. Twitter/X Thread (10 tweets)
    results["twitter_thread"] = generate_and_save(
        product, affiliate_link, product_dir,
        "twitter_thread.md", generate_twitter_thread
    )

    # 7. Instagram Captions (5 variations)
    results["instagram"] = generate_and_save(
        product, affiliate_link, product_dir,
        "instagram_captions.md", generate_instagram_captions
    )

    # 8. TikTok/Reel Scripts (3 scripts)
    results["tiktok_scripts"] = generate_and_save(
        product, affiliate_link, product_dir,
        "tiktok_scripts.md", generate_tiktok_scripts
    )

    # 9. YouTube Video Script
    results["youtube_script"] = generate_and_save(
        product, affiliate_link, product_dir,
        "youtube_script.md", generate_youtube_script
    )

    # 10. Email Newsletter
    results["newsletter"] = generate_and_save(
        product, affiliate_link, product_dir,
        "newsletter.md", generate_newsletter
    )

    # 11. Reddit-style Comments (10 variations)
    results["reddit_comments"] = generate_and_save(
        product, affiliate_link, product_dir,
        "reddit_comments.md", generate_reddit_comments
    )

    # 12. Quora Answers (5 variations)
    results["quora_answers"] = generate_and_save(
        product, affiliate_link, product_dir,
        "quora_answers.md", generate_quora_answers
    )

    # 13. Pinterest Pins (5 descriptions)
    results["pinterest"] = generate_and_save(
        product, affiliate_link, product_dir,
        "pinterest_pins.md", generate_pinterest
    )

    # 14. Facebook Posts (5 variations)
    results["facebook"] = generate_and_save(
        product, affiliate_link, product_dir,
        "facebook_posts.md", generate_facebook_posts
    )

    # 15. Deal Alert Templates
    results["deal_alerts"] = generate_and_save(
        product, affiliate_link, product_dir,
        "deal_alerts.md", generate_deal_alerts
    )

    # Save manifest
    manifest = {
        "product": product["title"],
        "link": affiliate_link,
        "generated_at": datetime.utcnow().isoformat(),
        "content_count": len([r for r in results.values() if r]),
        "files": {k: v for k, v in results.items() if v},
    }
    with open(os.path.join(product_dir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[PUMP] ✅ Generated {manifest['content_count']}/15 content pieces")
    print(f"[PUMP] 📁 Output: {product_dir}")
    return manifest


def generate_and_save(product, link, output_dir, filename, generator_fn):
    """Run a generator function and save the output"""
    try:
        content = generator_fn(product, link)
        if content:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  ✅ {filename}")
            return filename
    except Exception as e:
        print(f"  ❌ {filename}: {e}")
    return None


def ai_generate(system_prompt, user_prompt, max_tokens=2000):
    """Helper to call OpenAI"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.75,
    )
    return response.choices[0].message.content


def product_context(product, link):
    """Build product context string"""
    features = "\n".join(f"- {f}" for f in product.get("features", [])[:8])
    return f"""
Product: {product['title']}
Price: ${product.get('price', 'Check price')}
Rating: {product.get('rating', 'N/A')}
Features:
{features}
Affiliate Link: {link}
"""


def slugify(text):
    s = text.lower()
    s = "".join(c if c.isalnum() or c == " " else "" for c in s)
    return s.strip().replace("  ", " ").replace(" ", "-")[:60]


# ============================================================
# Content Generators (15 types)
# ============================================================

def generate_blog_review(product, link):
    return ai_generate(
        "You are an expert tech blogger. Write detailed, SEO-optimized product reviews.",
        f"Write a comprehensive 1500-2000 word product review in Markdown.\n{product_context(product, link)}\n"
        "Include: intro, features breakdown, pros/cons, who it's for, verdict, FAQ (5 questions), CTA with link.",
        max_tokens=4000,
    )

def generate_short_post(product, link):
    return ai_generate(
        "You write concise, engaging blog posts optimized for quick reads.",
        f"Write a 500-word quick review blog post in Markdown.\n{product_context(product, link)}\n"
        "Punchy, scannable, with bold key points. Include affiliate link twice.",
        max_tokens=1200,
    )

def generate_comparison(product, link):
    return ai_generate(
        "You write balanced product comparison articles for tech buyers.",
        f"Write a 1200-word comparison article: this product vs 3 competitors.\n{product_context(product, link)}\n"
        "Use a comparison table (Markdown), highlight where this product wins. Be fair but favor this product.",
        max_tokens=3000,
    )

def generate_buyers_guide(product, link):
    category = product.get("title", "").split()[0:3]
    return ai_generate(
        "You write comprehensive buyer's guides that help people make informed decisions.",
        f"Write a 1500-word buyer's guide for {' '.join(category)} products.\n{product_context(product, link)}\n"
        "Cover: what to look for, key specs explained, budget tiers, top pick (this product), alternatives.",
        max_tokens=3500,
    )

def generate_top_reasons(product, link):
    return ai_generate(
        "You write engaging listicle articles.",
        f"Write '10 Reasons Why [Product] Is Worth Every Penny' article.\n{product_context(product, link)}\n"
        "Each reason: catchy subheading + 100 words. Include affiliate link 3 times.",
        max_tokens=2500,
    )

def generate_twitter_thread(product, link):
    return ai_generate(
        "You write viral Twitter/X threads about tech products.",
        f"Write a 10-tweet thread reviewing this product.\n{product_context(product, link)}\n"
        "Tweet 1: hook. Tweets 2-9: key points, tips, comparisons. Tweet 10: CTA with link. Include hashtags.",
        max_tokens=1500,
    )

def generate_instagram_captions(product, link):
    return ai_generate(
        "You write engaging Instagram captions with emojis and hashtags.",
        f"Write 5 different Instagram caption variations for this product.\n{product_context(product, link)}\n"
        "Mix: review style, lifestyle, deal alert, unboxing, comparison. 30 hashtags per post. Include 'link in bio'.",
        max_tokens=2000,
    )

def generate_tiktok_scripts(product, link):
    return ai_generate(
        "You write viral TikTok/Reels scripts for tech content.",
        f"Write 3 short-form video scripts (30-60 seconds each) for this product.\n{product_context(product, link)}\n"
        "Include: hook (first 3 seconds), visual directions, voiceover text, CTA. Make them engaging and trendy.",
        max_tokens=2000,
    )

def generate_youtube_script(product, link):
    return ai_generate(
        "You write professional YouTube review scripts.",
        f"Write a 5-minute YouTube review script for this product.\n{product_context(product, link)}\n"
        "Include: intro hook, B-roll suggestions, specs walkthrough, real-world tests, verdict, CTA with link in description.",
        max_tokens=3000,
    )

def generate_newsletter(product, link):
    return ai_generate(
        "You write compelling email newsletters for deal hunters.",
        f"Write an email newsletter featuring this product as the top pick.\n{product_context(product, link)}\n"
        "Include: subject line (3 options), preview text, body with product highlight, CTA button text, P.S. line.",
        max_tokens=1500,
    )

def generate_reddit_comments(product, link):
    return ai_generate(
        "You write authentic, helpful Reddit comments. Never sound promotional.",
        f"Write 10 different Reddit comment variations recommending this product.\n{product_context(product, link)}\n"
        "Each should respond to a different scenario (budget question, comparison question, upgrade question, etc). "
        "Sound like a real person sharing experience. Vary tone and length. Include link naturally.",
        max_tokens=3000,
    )

def generate_quora_answers(product, link):
    return ai_generate(
        "You write detailed, authoritative Quora answers.",
        f"Write 5 Quora-style answers recommending this product.\n{product_context(product, link)}\n"
        "Each answers a different question (e.g., 'Best desktop under $1000?', 'Mac vs PC for students?'). "
        "Detailed, personal experience tone, 200-300 words each.",
        max_tokens=3000,
    )

def generate_pinterest(product, link):
    return ai_generate(
        "You write keyword-rich Pinterest pin descriptions.",
        f"Write 5 Pinterest pin descriptions for this product.\n{product_context(product, link)}\n"
        "Each: catchy title, keyword-rich description (200 chars), relevant hashtags. Different angles.",
        max_tokens=1200,
    )

def generate_facebook_posts(product, link):
    return ai_generate(
        "You write engaging Facebook posts for tech communities and marketplace.",
        f"Write 5 Facebook post variations for this product.\n{product_context(product, link)}\n"
        "Mix: review, deal alert, question-style engagement, comparison, personal recommendation. Conversational.",
        max_tokens=2000,
    )

def generate_deal_alerts(product, link):
    return ai_generate(
        "You write urgent, exciting deal alert posts.",
        f"Write 5 deal alert templates for different platforms.\n{product_context(product, link)}\n"
        "Include: Reddit deal post, Twitter deal alert, Facebook deal share, Discord deal message, Slickdeals-style post. "
        "Use urgency and value emphasis.",
        max_tokens=1500,
    )


# ============================================================
# Main
# ============================================================

def pump_all_links(links_file="links.txt"):
    """Process all links and generate maximum content"""
    if not os.path.exists(links_file):
        print(f"[ERROR] {links_file} not found.")
        return

    with open(links_file, "r") as f:
        links = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"[PUMP] 🚀 Content Pump starting — {len(links)} products")
    print(f"[PUMP] Generating 15 content types per product...")
    print(f"[PUMP] Estimated output: {len(links) * 15} pieces of content\n")

    all_results = []
    for i, link in enumerate(links, 1):
        print(f"\n{'='*60}")
        print(f"[PUMP] Product {i}/{len(links)}: {link}")
        print(f"{'='*60}")

        product = scrape_product(link)
        if not product:
            print(f"[SKIP] Could not scrape: {link}")
            continue

        manifest = generate_all_content(product, link)
        all_results.append(manifest)

    # Final summary
    total = sum(r.get("content_count", 0) for r in all_results)
    print(f"\n{'='*60}")
    print(f"[PUMP] 🎉 COMPLETE!")
    print(f"[PUMP] Products processed: {len(all_results)}")
    print(f"[PUMP] Total content pieces: {total}")
    print(f"[PUMP] Output directory: {OUTPUT_DIR}/")
    print(f"{'='*60}")


if __name__ == "__main__":
    pump_all_links()
