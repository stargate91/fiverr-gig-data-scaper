import time
import requests
import re
import os
import json
from dataclasses import dataclass
from typing import Optional, List, Dict
from bs4 import BeautifulSoup
from datetime import datetime
from dataclasses import asdict

@dataclass
class GigData:
    gig_url: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    subcategory2: Optional[str] = None
    seller_level: Optional[str] = None
    orders_in_queue: Optional[str] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    description: Optional[str] = None

    favorites: Optional[int] = None
    packages: Optional[Dict[str, dict]] = None
    hourly_rate: Optional[str] = None

    faqs: Optional[List[Dict[str, str]]] = None

    snapshot_time: Optional[str] = None

def parse_gig_url(soup: BeautifulSoup) -> Optional[str]:
    tag = soup.select_one('meta[property="og:url"]')
    return tag["content"] if tag and tag.has_attr("content") else None

def parse_breadcrumbs(soup: BeautifulSoup) -> tuple[Optional[str], Optional[str], Optional[str]]:
    nav = soup.select_one('nav[aria-label="breadcrumbs"]')
    if not nav:
        return None, None, None
    labels = [a.get_text(strip=True) for a in nav.select("a")][1:]
    return (
        labels[0] if len(labels) > 0 else None,
        labels[1] if len(labels) > 1 else None,
        labels[2] if len(labels) > 2 else None,
    )

def parse_seller_level(soup: BeautifulSoup) -> Optional[str]:
    possible_tags = soup.find_all("p", string=True)
    for tag in possible_tags:
        text = tag.get_text(strip=True)
        if any(level in text for level in ["Top Rated", "Level 2", "Level 1"]):
            return text
    return None

def parse_orders_in_queue(soup: BeautifulSoup) -> Optional[int]:
    tag = soup.find("p", string=lambda t: t and "orders in queue" in t)
    if not tag:
        return None

    match = re.search(r"\d+", tag.get_text())
    return int(match.group()) if match else None

def parse_rating_and_reviews(soup: BeautifulSoup) -> tuple[Optional[float], Optional[int]]:
    rating_tag = soup.select_one('div[data-track-tag="rating"] strong')
    rating = float(rating_tag.get_text(strip=True)) if rating_tag else None

    reviews = None
    review_tags = soup.select('div[data-track-tag="rating"] span[data-track-tag="text"]')
    for tag in review_tags:
        text = tag.get_text(strip=True)
        if "review" in text.lower():
            match = re.search(r'[\d,]+', text)
            if match:
                reviews = int(match.group(0).replace(",", ""))
            break
            
    return rating, reviews

def parse_description(soup: BeautifulSoup) -> Optional[str]:
    desc_div = soup.select_one('div.description-content')

    if not desc_div:
        return None

    text = desc_div.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    return clean_text

def parse_favorites(soup: BeautifulSoup) -> Optional[int]:
    tag = soup.select_one("span.collect-count")
    if not tag:
        return None
    try:
        return int(tag.get_text(strip=True).replace(",", ""))
    except ValueError:
        return None

def parse_packages(soup: BeautifulSoup) -> Dict[str, dict]:
    packages = {}

    package_blocks = soup.select("div.package-content")
    tab_labels = soup.select("div.nav-container label")

    for idx, block in enumerate(package_blocks):
        name = tab_labels[idx].get_text(strip=True) if idx < len(tab_labels) else f"package_{idx}"

        title = block.select_one("h3 b")
        price = block.select_one("span[data-track-tag='text']")
        description = block.select_one("header p")
        delivery = block.select_one(".delivery")
        revisions = block.select_one(".revisions")

        features = [
            li.get_text(strip=True)
            for li in block.select("ul.features li")
        ]

        packages[name] = {
            "title": title.get_text(strip=True) if title else None,
            "price": price.get_text(strip=True) if price else None,
            "description": description.get_text(strip=True) if description else None,
            "delivery_time": delivery.get_text(strip=True) if delivery else None,
            "revisions": revisions.get_text(strip=True) if revisions else None,
            "features": features,
        }

    return packages

def parse_hourly_rate(soup: BeautifulSoup) -> Optional[str]:
    tag = soup.find("p", string=lambda t: t and "/hour" in t)
    return tag.get_text(strip=True) if tag else None

def parse_faq(soup: BeautifulSoup) -> List[Dict[str, str]]:
    faqs = []

    faq_articles = soup.select("article.faq-collapsible")

    for article in faq_articles:
        question_tag = article.select_one(".faq-collapsible-title p")
        answer_tag = article.select_one(".faq-collapsible-content p")

        if not question_tag or not answer_tag:
            continue

        question = question_tag.get_text(strip=True)
        answer = answer_tag.get_text(separator="\n", strip=True)

        faqs.append({
            "question": question,
            "answer": answer
        })

    return faqs


def scrape_gig(url: str) -> GigData:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
    }
    time.sleep(6)
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    gig_url = parse_gig_url(soup)
    category, subcategory, subcategory2 = parse_breadcrumbs(soup)
    seller_level = parse_seller_level(soup) or "New Seller"
    orders_in_queue = parse_orders_in_queue(soup)
    rating, reviews = parse_rating_and_reviews(soup)
    description = parse_description(soup)
    favorites = parse_favorites(soup)
    packages = parse_packages(soup)
    hourly_rate = parse_hourly_rate(soup)
    faqs = parse_faq(soup)
    snapshot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
    
    return GigData(
        gig_url=gig_url,
        category=category,
        subcategory=subcategory,
        subcategory2=subcategory2,
        seller_level=seller_level,
        orders_in_queue=orders_in_queue,
        rating=rating,
        reviews=reviews,
        description=description,
        favorites=favorites,
        packages=packages,
        hourly_rate=hourly_rate,
        faqs=faqs,
        snapshot_time=snapshot_time
    )

def print_gig_pretty(gig: GigData):
    print(
        json.dumps(
            asdict(gig),
            indent=2,
            ensure_ascii=False
        )
    )

JSON_FILE = "gigs.json"

def save_gig_to_json(gig: GigData):
    data = []

    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(asdict(gig))

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False
        )

