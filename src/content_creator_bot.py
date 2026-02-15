# content_creator_bot.py - Automate content generation and posting

import random

# Sample templates for content
CONTENT_TEMPLATES = {
    "blog": "Check out our latest product: {product}! It features {features}.",
    "tweet": "Loving our new {product}! Available now! {url}",
    "pin": "Explore the amazing {product}. It's perfect for {use_case}! Learn more: {url}",
    "instagram": "✨ {product} ✨ Just what you need for {use_case}! Shop now: {url}"
}

def generate_content(product, content_type, **kwargs):
    """Generate content for a specific platform."""
    template = CONTENT_TEMPLATES.get(content_type, "")
    if not template:
        return f"No template available for content type: {content_type}"
    return template.format(product=product, **kwargs)

def post_content(platform, content):
    """Simulate posting content to a platform."""
    # Placeholder for actual posting logic (e.g., API calls)
    return f"Content posted to {platform}: {content}"

if __name__ == "__main__":
    # Example usage
    product = "Cool Gadget 3000"
    feature_list = "advanced AI and sleek design"
    use_case = "tech enthusiasts"
    url = "http://shop.now/gadget"

    platforms = ["blog", "tweet", "pin", "instagram"]
    for platform in platforms:
        content = generate_content(product, platform, features=feature_list, url=url, use_case=use_case)
        print(post_content(platform, content))