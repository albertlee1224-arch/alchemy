"""Slack Bot — 메시지 전송 및 이모지 인터랙션 처리"""

import os
import re
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask, request

from src.bot.formatter import (
    format_daily_header, format_single_news, format_deep_read_header,
    format_single_article, format_weekend_header, format_weekly_report,
)
from src.curator.preferences import get_supabase_client, save_feedback


def _save_to_notion(supabase, url: str, rating: str):
    """Supabase에서 아티클/뉴스 정보를 찾아 Notion Vault에 저장"""
    try:
        from src.vault.notion import add_article_to_vault, add_news_to_vault

        # 아티클 테이블에서 먼저 검색
        result = supabase.table("articles").select("*").eq("url", url).execute()
        if result.data:
            add_article_to_vault(result.data[0], rating)
            return

        # 뉴스 테이블에서 검색
        result = supabase.table("news").select("*").eq("url", url).execute()
        if result.data:
            add_news_to_vault(result.data[0], rating)
            return

        # DB에 없으면 최소 정보로 저장
        add_article_to_vault({"title": "Untitled", "url": url}, rating)
    except Exception as e:
        print(f"Notion save error: {e}")


def _post(client, channel, text, blocks):
    """공통 메시지 전송 — 링크 프리뷰 비활성화"""
    client.chat_postMessage(
        channel=channel,
        text=text,
        blocks=blocks,
        unfurl_links=False,
        unfurl_media=False,
    )


def create_slack_app():
    """Slack Bolt 앱 생성"""
    app = App(
        token=os.environ["SLACK_BOT_TOKEN"],
        signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    )

    supabase = get_supabase_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )

    @app.event("reaction_added")
    def handle_reaction(event, client):
        """이모지 반응 처리 — ⭐📂👎"""
        reaction = event.get("reaction", "")
        channel = event.get("item", {}).get("channel", "")
        message_ts = event.get("item", {}).get("ts", "")

        reaction_map = {
            "star": "star",
            "file_folder": "bookmark",
            "-1": "thumbsdown",
            "thumbsdown": "thumbsdown",
        }

        if reaction not in reaction_map:
            return

        try:
            result = client.conversations_history(
                channel=channel,
                latest=message_ts,
                inclusive=True,
                limit=1,
            )
            if result["messages"]:
                message = result["messages"][0]
                text = str(message.get("blocks", ""))
                urls = re.findall(r'https?://[^\s|>\'\"]+', text)

                if urls:
                    save_feedback(supabase, urls[0], reaction_map[reaction])

                # Notion Vault에 저장 (⭐, 📂만)
                if reaction in ("star", "file_folder"):
                    _save_to_notion(supabase, urls[0] if urls else "", reaction_map[reaction])

                emoji_labels = {
                    "star": "⭐ Notion Vault에 아카이브했어요!",
                    "file_folder": "📂 Notion Vault에 저장했어요!",
                    "-1": "👎 다음 추천에 반영할게요!",
                    "thumbsdown": "👎 다음 추천에 반영할게요!",
                }
                client.chat_postMessage(
                    channel=channel,
                    thread_ts=message_ts,
                    text=emoji_labels.get(reaction, "피드백 저장!"),
                )
        except Exception as e:
            print(f"Reaction handling error: {e}")

    return app


def send_daily_briefing(news: list, articles: list):
    """데일리 브리핑 — 모든 콘텐츠 개별 메시지"""
    from slack_sdk import WebClient
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel = os.environ.get("SLACK_CHANNEL_DAILY", "1_daily_briefing")

    # 1. 헤더
    _post(client, channel, "⚗️ ALCHEMY — Daily Briefing", format_daily_header())

    # 2. 뉴스 각각 개별 메시지
    for i, n in enumerate(news[:5]):
        _post(client, channel, f"📡 {n.get('title', '')}", format_single_news(n, i))

    # 3. Deep Read 섹션 헤더 (Connector의 관통하는 질문 포함)
    daily_connection = ""
    if articles and articles[0].get("daily_connection"):
        daily_connection = articles[0]["daily_connection"]
    _post(client, channel, "📖 TODAY'S DEEP READ", format_deep_read_header(daily_connection))

    # 4. 아티클 각각 개별 메시지
    for i, article in enumerate(articles[:3]):
        _post(client, channel, f"📖 {article.get('title', '')}", format_single_article(article, i))


def send_weekend_deep_dive(articles: list, weekly_connection: str = ""):
    """Weekend Deep Dive — 헤더 + 아티클 각각 개별"""
    from slack_sdk import WebClient
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel = os.environ.get("SLACK_CHANNEL_WEEKEND", "2_weekend_read")

    _post(client, channel, "📚 ALCHEMY — Weekend Deep Dive", format_weekend_header(weekly_connection))

    for i, article in enumerate(articles[:3]):
        _post(client, channel, f"📖 {article.get('title', '')}", format_single_article(article, i))


def send_weekly_report(stats: dict):
    """주간 리포트"""
    from slack_sdk import WebClient
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    channel = os.environ.get("SLACK_CHANNEL_REPORT", "3_report")

    _post(client, channel, "📊 ALCHEMY — Weekly Report", format_weekly_report(stats))


def create_flask_app():
    """Flask 앱 (Slack 이벤트 수신용)"""
    flask_app = Flask(__name__)
    slack_app = create_slack_app()
    handler = SlackRequestHandler(slack_app)

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        return handler.handle(request)

    @flask_app.route("/health", methods=["GET"])
    def health():
        return "OK", 200

    return flask_app
