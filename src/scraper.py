"""
Amazon Product Scraper
Extracts product details from Amazon affiliate links.
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
}


def scrape_product(url):
    """Scrape product details from an Amazon URL"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        product = {
            "url": url,
            "title": extract_title(soup),
            "price": extract_price(soup),
            "rating": extract_rating(soup),
            "features": extract_features(soup),
            "image_url": extract_image(soup),
            "description": extract_description(soup),
        }

        if not product["title"]:
            return None

        return product

    except Exception as e:
        print(f"[ERROR] Scraping failed for {url}: {e}")
        return None


def extract_title(soup):
    """Extract product title"""
    tag = soup.find("span", {"id": "productTitle"})
    return tag.get_text(strip=True) if tag else None


def extract_price(soup):
    """Extract product price"""
    tag = soup.find("span", {"class": "a-price-whole"})
    if tag:
        fraction = soup.find("span", {"class": "a-price-fraction"})
        price = tag.get_text(strip=True).replace(",", "")
        if fraction:
            price += fraction.get_text(strip=True)
        return price
    return None


def extract_rating(soup):
    """Extract product rating"""
    tag = soup.find("span", {"class": "a-icon-alt"})
    return tag.get_text(strip=True) if tag else None


def extract_features(soup):
    """Extract product feature bullet points"""
    bullets = soup.find("div", {"id": "feature-bullets"})
    if bullets:
        items = bullets.find_all("span", {"class": "a-list-item"})
        return [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
    return []


def extract_image(soup):
    """Extract main product image URL"""
    tag = soup.find("img", {"id": "landingImage"})
    if tag:
        return tag.get("data-old-hires") or tag.get("src")
    return None


def extract_description(soup):
    """Extract product description"""
    tag = soup.find("div", {"id": "productDescription"})
    return tag.get_text(strip=True) if tag else ""
