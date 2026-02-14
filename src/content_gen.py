"""
AI-Powered Content Generator
Uses local Ollama models (free) or OpenAI as fallback.
"""

import os
from ai_provider import ai_generate


def generate_content(product):
    """Generate marketing content for a product using AI"""
    try:
        prompt = build_prompt(product)

        ai_text = ai_generate(
            system_prompt=(
                "You are a skilled affiliate marketer. Write engaging, "
                "authentic product recommendations. Be conversational, "
                "highlight key benefits, and include a clear call-to-action. "
                "Never sound spammy. Include relevant hashtags for social media."
            ),
            user_prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
        )

        if not ai_text:
            return None

        # Parse AI response into structured content
        content = parse_ai_response(ai_text, product)
        return content

    except Exception as e:
        print(f"[ERROR] Content generation failed: {e}")
        return None


def build_prompt(product):
    """Build the prompt for AI content generation"""
    features_text = "\n".join(f"- {f}" for f in product.get("features", [])[:5])

    return f"""
Create marketing content for this Amazon product:

**Title:** {product['title']}
**Price:** ${product.get('price', 'Check price')}
**Rating:** {product.get('rating', 'N/A')}
**Key Features:**
{features_text}

Generate:
1. A catchy Reddit post title (under 100 chars)
2. A Reddit post body (200-300 words, helpful and authentic)
3. A short Twitter/X post (under 280 chars with hashtags)
4. A blog paragraph (150-200 words)

Format each section with headers: [REDDIT_TITLE], [REDDIT_BODY], [TWEET], [BLOG]
Include the product link placeholder: {{PRODUCT_LINK}}
"""


def parse_ai_response(text, product):
    """Parse AI-generated text into structured content"""
    sections = {}
    current_section = None
    current_text = []

    for line in text.split("\n"):
        line_stripped = line.strip()
        if line_stripped.startswith("[") and line_stripped.endswith("]"):
            if current_section:
                sections[current_section] = "\n".join(current_text).strip()
            current_section = line_stripped[1:-1]
            current_text = []
        else:
            current_text.append(line)

    if current_section:
        sections[current_section] = "\n".join(current_text).strip()

    # Replace link placeholder
    for key in sections:
        sections[key] = sections[key].replace("{{PRODUCT_LINK}}", product["url"])

    return {
        "reddit_title": sections.get("REDDIT_TITLE", product["title"]),
        "post_body": sections.get("REDDIT_BODY", ""),
        "tweet": sections.get("TWEET", ""),
        "blog": sections.get("BLOG", ""),
        "product": product,
    }
