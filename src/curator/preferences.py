"""사용자 취향 관리 모듈 — 👎 피드백 기반 + 중복 방지"""

from supabase import create_client
from datetime import datetime, timedelta
from typing import List, Optional


def get_supabase_client(url: str, key: str):
    """Supabase 클라이언트 생성"""
    return create_client(url, key)


def save_article(client, article: dict, briefing_type: str = "daily"):
    """추천된 아티클을 DB에 저장"""
    data = {
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "source": article.get("source", ""),
        "axis_id": article.get("axis_id"),
        "axis_name": article.get("axis_name", ""),
        "why_new": article.get("why_new", ""),
        "new_concept_name": article.get("new_concept_name", ""),
        "new_concept_desc": article.get("new_concept_desc", ""),
        "why_read": article.get("why_read", ""),
        "read_time": article.get("read_time", ""),
        "briefing_type": briefing_type,
        "status": "sent",
    }
    result = client.table("articles").insert(data).execute()
    return result.data[0] if result.data else None


def save_news(client, news: dict):
    """뉴스 아이템을 DB에 저장"""
    data = {
        "title": news.get("title", ""),
        "url": news.get("url", ""),
        "source": news.get("source", ""),
        "hashtag": news.get("hashtag", ""),
        "summary_line_1": news.get("summary_line_1", ""),
        "summary_line_2": news.get("summary_line_2", ""),
        "summary_line_3": news.get("summary_line_3", ""),
        "status": "sent",
    }
    result = client.table("news").insert(data).execute()
    return result.data[0] if result.data else None


def save_feedback(client, article_url: str, reaction: str, memo: str = ""):
    """이모지 피드백 저장"""
    data = {
        "article_url": article_url,
        "reaction": reaction,
        "memo": memo,
    }
    # articles 테이블 상태 업데이트
    status_map = {"star": "starred", "bookmark": "archived", "thumbsdown": "skipped"}
    new_status = status_map.get(reaction, "sent")

    client.table("articles").update({"status": new_status}).eq("url", article_url).execute()
    client.table("feedback").insert(data).execute()


def get_recent_urls(client, days: int = 7) -> set:
    """최근 N일 내 추천된 아티클/뉴스 URL 목록 (중복 방지용)"""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    recent_urls = set()

    articles = client.table("articles").select("url").gte("created_at", cutoff).execute()
    for a in (articles.data or []):
        if a.get("url"):
            recent_urls.add(a["url"])

    news = client.table("news").select("url").gte("created_at", cutoff).execute()
    for n in (news.data or []):
        if n.get("url"):
            recent_urls.add(n["url"])

    return recent_urls


def get_excluded_topics(client) -> List[str]:
    """👎 피드백에서 제외할 토픽 패턴 추출"""
    result = client.table("feedback").select("*").eq("reaction", "thumbsdown").execute()

    if not result.data:
        return []

    # 👎 받은 아티클의 axis, source 패턴 분석
    skipped_axes = {}
    skipped_sources = {}

    for fb in result.data:
        url = fb.get("article_url", "")
        # 해당 아티클 정보 조회
        article = client.table("articles").select("*").eq("url", url).execute()
        if article.data:
            a = article.data[0]
            axis = a.get("axis_name", "")
            source = a.get("source", "")
            if axis:
                skipped_axes[axis] = skipped_axes.get(axis, 0) + 1
            if source:
                skipped_sources[source] = skipped_sources.get(source, 0) + 1

    # 3회 이상 👎 받은 토픽/소스 제외
    excluded = []
    for topic, count in skipped_axes.items():
        if count >= 3:
            excluded.append(f"Axis: {topic}")
    for source, count in skipped_sources.items():
        if count >= 3:
            excluded.append(f"Source: {source}")

    return excluded


def get_weekly_stats(client) -> dict:
    """주간 통계"""
    from datetime import datetime, timedelta
    week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()

    # 이번 주 추천된 아티클
    articles = client.table("articles").select("*").gte("created_at", week_ago).execute()

    # 이번 주 피드백
    feedback = client.table("feedback").select("*").gte("created_at", week_ago).execute()

    total = len(articles.data) if articles.data else 0
    starred = len([a for a in (articles.data or []) if a.get("status") == "starred"])
    archived = len([a for a in (articles.data or []) if a.get("status") == "archived"])
    skipped = len([a for a in (articles.data or []) if a.get("status") == "skipped"])

    # Axis별 통계
    axis_counts = {}
    for a in (articles.data or []):
        axis = a.get("axis_name", "Unknown")
        axis_counts[axis] = axis_counts.get(axis, 0) + 1

    starred_articles = [a for a in (articles.data or []) if a.get("status") == "starred"]

    return {
        "total": total,
        "starred": starred,
        "archived": archived,
        "skipped": skipped,
        "axis_counts": axis_counts,
        "starred_articles": starred_articles,
    }
