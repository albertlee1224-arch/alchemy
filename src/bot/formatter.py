"""Slack 메시지 포맷터 — 메시지 분절 방식"""

from datetime import datetime
from typing import List, Dict


def format_daily_header() -> List[Dict]:
    """데일리 브리핑 헤더만 (1개 메시지)"""
    today = datetime.now().strftime("%Y.%m.%d (%a)")

    return [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "⚗️ ALCHEMY — Daily Briefing"}
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"{today} · 06:30 AM"}]
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*📡 GLOBAL PULSE — 5 Headlines*"}
        },
    ]


def format_single_news(news: Dict, index: int) -> List[Dict]:
    """개별 뉴스 카드 (1개 메시지)"""
    hashtag = news.get("hashtag", "")
    title = news.get("title", "")
    line1 = news.get("summary_line_1", "")
    line2 = news.get("summary_line_2", "")
    line3 = news.get("summary_line_3", "")
    url = news.get("url", "")

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{index + 1}. {hashtag}  {title}*\n"
                    f"{line1}\n"
                    f"{line2}\n"
                    f"{line3}\n"
                    f"<{url}|🔗 기사 보기>"
                )
            }
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "⭐ 인상적  ·  📂 저장  ·  👎 관심없음"}]
        },
    ]


def format_deep_read_header(daily_connection: str = "") -> List[Dict]:
    """Deep Read 섹션 헤더 + 관통하는 질문 (1개 메시지)"""
    blocks = [
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "*📖 TODAY'S DEEP READ — 3 Picks*"}
        },
    ]

    if daily_connection:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*🔗 오늘의 브리핑을 관통하는 질문:*\n_{daily_connection}_"}
        })
        blocks.append({"type": "divider"})

    return blocks


def format_single_article(article: Dict, index: int) -> List[Dict]:
    """개별 아티클 카드 (1개 메시지)"""
    title = article.get("title", "")
    source = article.get("source", "")
    read_time = article.get("read_time", "")
    url = article.get("url", "")
    why_new = article.get("why_new", "")
    concept_name = article.get("new_concept_name", "")
    concept_desc = article.get("new_concept_desc", "")
    why_read = article.get("why_read", "")

    number_emoji = ["1️⃣", "2️⃣", "3️⃣"][index]

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{number_emoji} *<{url}|{title}>*\n"
                    f"_{source} · {read_time}_"
                )
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"🆕 *왜 새로운가*\n{why_new}\n\n"
                    f"💎 *새로운 개념*\n*{concept_name}* — {concept_desc}\n\n"
                    f"🎯 *왜 읽어야 하는가*\n{why_read}"
                )
            }
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "⭐ 인상적  ·  📂 저장  ·  👎 관심없음"}]
        },
    ]


def format_weekend_header(weekly_connection: str = "") -> List[Dict]:
    """Weekend Deep Dive 헤더 (1개 메시지)"""
    today = datetime.now().strftime("%Y.%m.%d (%a)")

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📚 ALCHEMY — Weekend Deep Dive"}
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"{today} · 06:30 AM"}]
        },
        {"type": "divider"},
    ]

    if weekly_connection:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*이번 주를 관통하는 질문:*\n_{weekly_connection}_"}
        })
        blocks.append({"type": "divider"})

    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": "*🏔️ WEEKEND PICKS — 주말에 깊이 읽을 3편*"}
    })

    return blocks


def format_weekly_report(stats: dict) -> List[Dict]:
    """일요일 주간 리포트 메시지"""
    today = datetime.now().strftime("%Y.%m.%d (%a)")
    week_num = datetime.now().isocalendar()[1]

    total = stats.get("total", 0)
    starred = stats.get("starred", 0)
    archived = stats.get("archived", 0)
    skipped = stats.get("skipped", 0)
    axis_counts = stats.get("axis_counts", {})
    starred_articles = stats.get("starred_articles", [])

    axis_text = ""
    if axis_counts:
        sorted_axes = sorted(axis_counts.items(), key=lambda x: x[1], reverse=True)
        most = sorted_axes[0] if sorted_axes else ("없음", 0)
        least = sorted_axes[-1] if sorted_axes else ("없음", 0)
        axis_lines = "\n".join([f"  • {name}: {count}편" for name, count in sorted_axes])
        axis_text = f"*Axis별 분포:*\n{axis_lines}\n\n📈 가장 관심 높은 Axis: *{most[0]}* ({most[1]}편)\n📉 가장 적은 Axis: *{least[0]}* ({least[1]}편)"

    starred_text = ""
    if starred_articles:
        starred_lines = "\n".join([
            f"  • <{a.get('url', '')}|{a.get('title', '')}>" for a in starred_articles
        ])
        starred_text = f"\n\n*⭐ 이번 주 인상적인 아티클:*\n{starred_lines}"

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📊 ALCHEMY — Weekly Report"}
        },
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": f"Week {week_num}, {today} · 12:00 PM"}]
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*📈 이번 주 리딩 현황*\n"
                    f"• 제안된 아티클: *{total}편*\n"
                    f"• ⭐ 인상적: *{starred}편*\n"
                    f"• 📂 읽음: *{archived}편*\n"
                    f"• 👎 관심없음: *{skipped}편*"
                )
            }
        },
        {"type": "divider"},
    ]

    if axis_text:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": axis_text}
        })

    if starred_text:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": starred_text}
        })

    blocks.extend([
        {"type": "divider"},
        {
            "type": "context",
            "elements": [{"type": "mrkdwn", "text": "⚗️ _Alchemy by ALBOT — Weekly Report_"}]
        },
    ])

    return blocks
