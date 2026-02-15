"""Notion Vault — 아카이브 연동 모듈"""

import os
from notion_client import Client
from datetime import datetime


def get_notion_client():
    """Notion 클라이언트 초기화"""
    return Client(auth=os.environ["NOTION_API_KEY"])


def get_database_id():
    """Notion DB ID"""
    return os.environ.get(
        "NOTION_DB_ID", "308ea75a4d8980afa727fc7a5e0ced4c"
    )


def setup_database_properties(client=None):
    """Notion DB 속성 세팅 (최초 1회)"""
    if client is None:
        client = get_notion_client()

    db_id = get_database_id()

    client.databases.update(
        database_id=db_id,
        properties={
            "Title": {"title": {}},
            "URL": {"url": {}},
            "Source": {
                "select": {
                    "options": [
                        {"name": "Noema Magazine", "color": "purple"},
                        {"name": "Aeon", "color": "blue"},
                        {"name": "Psyche", "color": "pink"},
                        {"name": "MIT Technology Review", "color": "red"},
                        {"name": "The Atlantic", "color": "orange"},
                        {"name": "Works in Progress", "color": "yellow"},
                        {"name": "Quanta Magazine", "color": "green"},
                        {"name": "Paul Graham", "color": "gray"},
                        {"name": "Farnam Street", "color": "brown"},
                        {"name": "The Marginalian", "color": "default"},
                        {"name": "Seth Godin", "color": "default"},
                    ]
                }
            },
            "Axis": {
                "select": {
                    "options": [
                        {"name": "Cognition & AI", "color": "blue"},
                        {"name": "Deep Work", "color": "purple"},
                        {"name": "Embodied Intelligence", "color": "green"},
                        {"name": "Philosophy of Technology", "color": "orange"},
                        {"name": "The New Scholar", "color": "red"},
                    ]
                }
            },
            "New Concept": {"rich_text": {}},
            "Concept Note": {"rich_text": {}},
            "Why It Matters": {"rich_text": {}},
            "Rating": {
                "select": {
                    "options": [
                        {"name": "⭐ 인상적", "color": "yellow"},
                        {"name": "📂 저장", "color": "blue"},
                    ]
                }
            },
            "Date": {"date": {}},
            "Tags": {"multi_select": {"options": []}},
            "My Note": {"rich_text": {}},
        },
    )
    print("Notion DB properties configured!")


def add_article_to_vault(article: dict, rating: str = "📂 저장"):
    """아티클을 Notion Vault에 추가"""
    client = get_notion_client()
    db_id = get_database_id()

    # rating 매핑
    rating_label = "⭐ 인상적" if rating == "star" else "📂 저장"

    properties = {
        "Title": {
            "title": [{"text": {"content": article.get("title", "Untitled")}}]
        },
        "URL": {"url": article.get("url", "")},
        "Rating": {"select": {"name": rating_label}},
        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
    }

    # Source
    source = article.get("source", "")
    if source:
        properties["Source"] = {"select": {"name": source}}

    # Axis
    axis_name = article.get("axis_name", "")
    if axis_name:
        properties["Axis"] = {"select": {"name": axis_name}}

    # New Concept
    concept_name = article.get("new_concept_name", "")
    if concept_name:
        properties["New Concept"] = {
            "rich_text": [{"text": {"content": concept_name}}]
        }

    # Concept Note
    concept_desc = article.get("new_concept_desc", "")
    if concept_desc:
        properties["Concept Note"] = {
            "rich_text": [{"text": {"content": concept_desc}}]
        }

    # Why It Matters
    why_read = article.get("why_read", "")
    if why_read:
        properties["Why It Matters"] = {
            "rich_text": [{"text": {"content": why_read}}]
        }

    result = client.pages.create(parent={"database_id": db_id}, properties=properties)
    print(f"Added to Notion Vault: {article.get('title', '')}")
    return result


def add_news_to_vault(news: dict, rating: str = "📂 저장"):
    """뉴스를 Notion Vault에 추가"""
    client = get_notion_client()
    db_id = get_database_id()

    rating_label = "⭐ 인상적" if rating == "star" else "📂 저장"

    # 뉴스 3줄 요약을 Why It Matters에 합침
    summary = "\n".join(filter(None, [
        news.get("summary_line_1", ""),
        news.get("summary_line_2", ""),
        news.get("summary_line_3", ""),
    ]))

    properties = {
        "Title": {
            "title": [{"text": {"content": news.get("title", "Untitled")}}]
        },
        "URL": {"url": news.get("url", "")},
        "Rating": {"select": {"name": rating_label}},
        "Date": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
    }

    source = news.get("source", "")
    if source:
        properties["Source"] = {"select": {"name": source}}

    if summary:
        properties["Why It Matters"] = {
            "rich_text": [{"text": {"content": summary[:2000]}}]
        }

    hashtag = news.get("hashtag", "")
    if hashtag:
        properties["Tags"] = {"multi_select": [{"name": hashtag}]}

    result = client.pages.create(parent={"database_id": db_id}, properties=properties)
    print(f"Added news to Notion Vault: {news.get('title', '')}")
    return result
