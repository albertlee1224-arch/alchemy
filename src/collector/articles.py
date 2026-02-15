"""Deep Read — RSS 기반 아티클 수집 모듈"""

import feedparser
import yaml
import os
from datetime import datetime, timedelta
from typing import List, Dict


def load_sources(config_path: str = None) -> List[Dict]:
    """소스 설정 파일 로드"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "sources.yml"
        )
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("deep_read_sources", [])


def collect_articles_from_rss(sources: List[Dict], hours: int = 48) -> List[Dict]:
    """RSS 피드에서 최근 아티클 수집"""
    articles = []
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    for source in sources:
        try:
            feed = feedparser.parse(source["url"])

            for entry in feed.entries[:10]:
                # 발행일 파싱
                published = entry.get("published_parsed") or entry.get("updated_parsed")
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date < cutoff:
                        continue
                else:
                    pub_date = datetime.utcnow()

                # 콘텐츠 추출
                content = ""
                if entry.get("content"):
                    content = entry.content[0].get("value", "")
                elif entry.get("summary"):
                    content = entry.summary

                # HTML 태그 간단 제거
                import re
                content = re.sub(r"<[^>]+>", "", content)
                content = content[:2000]  # 토큰 절약

                articles.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": source["name"],
                    "tier": source.get("tier", 3),
                    "content_preview": content,
                    "published_at": pub_date.isoformat(),
                    "type": "article",
                })
        except Exception as e:
            print(f"RSS error for {source['name']}: {e}")

    return articles


def collect_all_articles(config_path: str = None) -> List[Dict]:
    """전체 아티클 수집 통합"""
    sources = load_sources(config_path)
    articles = collect_articles_from_rss(sources)

    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique = []
    for article in articles:
        if article["url"] not in seen_urls and article["title"]:
            seen_urls.add(article["url"])
            unique.append(article)

    # Tier 순서로 정렬 (Tier 1 우선)
    unique.sort(key=lambda x: x.get("tier", 3))

    return unique
