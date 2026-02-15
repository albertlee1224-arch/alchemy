"""Global Pulse — 뉴스 수집 모듈"""

import httpx
import feedparser
import os
from datetime import datetime, timedelta
from typing import List, Dict


def collect_news_from_api(api_key: str, keywords: List[str], max_results: int = 50) -> List[Dict]:
    """NewsAPI에서 키워드 기반 뉴스 수집"""
    articles = []
    base_url = "https://newsapi.org/v2/everything"

    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    for keyword in keywords:
        try:
            response = httpx.get(
                base_url,
                params={
                    "q": keyword,
                    "from": yesterday,
                    "sortBy": "relevancy",
                    "language": "en",
                    "pageSize": 10,
                    "apiKey": api_key,
                },
                timeout=15,
            )
            if response.status_code == 200:
                data = response.json()
                for article in data.get("articles", []):
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "published_at": article.get("publishedAt", ""),
                        "keyword": keyword,
                        "type": "news",
                    })
        except Exception as e:
            print(f"NewsAPI error for '{keyword}': {e}")

    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article["url"] not in seen_urls and article["title"]:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    return unique_articles[:max_results]


def collect_news_from_google_rss(keywords: List[str], max_results: int = 30) -> List[Dict]:
    """Google News RSS에서 키워드 기반 뉴스 수집 (무료 백업)"""
    articles = []

    for keyword in keywords:
        try:
            query = keyword.replace(" ", "+")
            feed_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:5]:
                articles.append({
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", ""),
                    "url": entry.get("link", ""),
                    "source": entry.get("source", {}).get("title", "Google News"),
                    "published_at": entry.get("published", ""),
                    "keyword": keyword,
                    "type": "news",
                })
        except Exception as e:
            print(f"Google RSS error for '{keyword}': {e}")

    # 중복 제거
    seen_urls = set()
    unique_articles = []
    for article in articles:
        if article["url"] not in seen_urls and article["title"]:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    return unique_articles[:max_results]


def collect_all_news(api_key: str, keywords: List[str]) -> List[Dict]:
    """모든 소스에서 뉴스 수집 통합"""
    all_news = []

    # NewsAPI
    if api_key:
        all_news.extend(collect_news_from_api(api_key, keywords))

    # Google News RSS (무료 백업)
    all_news.extend(collect_news_from_google_rss(keywords))

    # 중복 제거
    seen_urls = set()
    unique = []
    for article in all_news:
        if article["url"] not in seen_urls:
            seen_urls.add(article["url"])
            unique.append(article)

    return unique
