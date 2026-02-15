# engagement_bot.py - Social listening and engagement

import random

# Sample keywords associated with buying intent
BUYING_KEYWORDS = ["buy", "purchase", "recommend", "wishlist", "need"]

# Mock monitored posts
SOCIAL_MEDIA_POSTS = [
    "Looking to buy a new phone. Any recommendations?",
    "What's the best tech gadget for 2026?",
    "I need a gift for someone who loves gadgets.",
    "Check out this cool tech product!",
    "Adding the Cool Gadget 3000 to my wishlist."
]

def detect_buying_intent(post):
    """Detects buying intent in a social media post based on keywords."""
    for keyword in BUYING_KEYWORDS:
        if keyword in post.lower():
            return True
    return False

def engage_with_post(post):
    """Engage with a post that has buying intent."""
    response = f"Thanks for your interest! You might love the Cool Gadget 3000. Check it out here: http://shop.now/gadget"
    return f"Engaged with post: '{post}' -> Response: '{response}'"

if __name__ == "__main__":
    for post in SOCIAL_MEDIA_POSTS:
        if detect_buying_intent(post):
            print(engage_with_post(post))