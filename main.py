"""Alchemy — 메인 실행 파일"""

import os
import sys
import yaml
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def notify_error(job_name: str, error: Exception):
    """에러 발생 시 Slack DM으로 알림"""
    try:
        from slack_sdk import WebClient
        client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        channel = os.environ.get("SLACK_CHANNEL_DAILY", "1_daily_briefing")
        error_msg = f"```{traceback.format_exc()[-500:]}```"
        client.chat_postMessage(
            channel=channel,
            text=(
                f"🚨 *Alchemy Error — {job_name}*\n"
                f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"{error_msg}"
            ),
        )
    except Exception:
        print(f"Failed to send error notification: {error}")


def load_config():
    """설정 파일 로드"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base_dir, "config", "sources.yml"), "r") as f:
        sources_config = yaml.safe_load(f)

    return sources_config


def run_daily_briefing():
    """매일 오전 06:30 — Daily Briefing"""
    from src.collector.news import collect_all_news
    from src.collector.articles import collect_all_articles
    from src.curator.summarizer import init_model, select_and_summarize_news, select_and_summarize_articles
    from src.curator.preferences import get_supabase_client, save_article, save_news, get_excluded_topics, get_recent_urls
    from src.bot.slack import send_daily_briefing

    try:
        print(f"[{datetime.now()}] Starting daily briefing...")

        config = load_config()

        # 1. 수집
        print("Collecting news...")
        news_keywords = config.get("news_keywords", [])
        raw_news = collect_all_news(
            api_key=os.environ.get("NEWS_API_KEY", ""),
            keywords=news_keywords,
        )
        print(f"  Collected {len(raw_news)} news articles")

        print("Collecting deep read articles...")
        raw_articles = collect_all_articles()
        print(f"  Collected {len(raw_articles)} articles")

        # 1.5. 중복 제거 (최근 7일 추천된 URL 제외)
        supabase = get_supabase_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"],
        )
        recent_urls = get_recent_urls(supabase, days=7)
        if recent_urls:
            raw_news = [n for n in raw_news if n.get("url") not in recent_urls]
            raw_articles = [a for a in raw_articles if a.get("url") not in recent_urls]
            print(f"  After dedup: {len(raw_news)} news, {len(raw_articles)} articles")

        # 2. AI 선별 + 요약
        print("Curating with Groq...")
        model = init_model(os.environ["GROQ_API_KEY"])

        excluded = get_excluded_topics(supabase)
        if excluded:
            print(f"  Excluding topics: {excluded}")

        selected_news = select_and_summarize_news(model, raw_news, count=5)
        print(f"  Selected {len(selected_news)} news")

        # ⭐ 아티클을 Connector 에이전트에 전달 (개인화 강화)
        from src.curator.preferences import get_weekly_stats
        stats = get_weekly_stats(supabase)
        starred = stats.get("starred_articles", [])

        selected_articles = select_and_summarize_articles(
            model, raw_articles, count=3,
            excluded_topics=excluded, starred_articles=starred
        )
        print(f"  Selected {len(selected_articles)} deep reads")

        # 3. DB 저장
        print("Saving to database...")
        for news in selected_news:
            save_news(supabase, news)
        for article in selected_articles:
            save_article(supabase, article, briefing_type="daily")

        # 4. Slack 전송
        print("Sending to Slack...")
        send_daily_briefing(selected_news, selected_articles)

        print(f"[{datetime.now()}] Daily briefing complete!")

    except Exception as e:
        print(f"Daily briefing error: {e}")
        notify_error("Daily Briefing", e)


def run_weekend_deep_dive():
    """토요일 오전 06:30 — Weekend Deep Dive"""
    from src.collector.articles import collect_all_articles
    from src.curator.summarizer import init_model
    from src.curator.preferences import get_supabase_client, save_article, get_excluded_topics, get_weekly_stats, get_recent_urls
    from src.reporter.weekly import generate_weekend_articles, generate_weekly_connection
    from src.bot.slack import send_weekend_deep_dive

    try:
        print(f"[{datetime.now()}] Starting weekend deep dive...")

        # 1. 수집 (48시간으로 확대)
        raw_articles = collect_all_articles()

        # 2. AI 선별
        model = init_model(os.environ["GROQ_API_KEY"])
        supabase = get_supabase_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_KEY"],
        )

        # 중복 제거
        recent_urls = get_recent_urls(supabase, days=7)
        if recent_urls:
            raw_articles = [a for a in raw_articles if a.get("url") not in recent_urls]
            print(f"  After dedup: {len(raw_articles)} articles")

        excluded = get_excluded_topics(supabase)
        selected_articles = generate_weekend_articles(model, raw_articles, count=3)

        # 3. 주간 연결고리 생성
        stats = get_weekly_stats(supabase)
        weekly_connection = generate_weekly_connection(model, stats.get("starred_articles", []))

        # 4. DB 저장
        for article in selected_articles:
            save_article(supabase, article, briefing_type="weekend")

        # 5. Slack 전송
        send_weekend_deep_dive(selected_articles, weekly_connection)

        print(f"[{datetime.now()}] Weekend deep dive complete!")

    except Exception as e:
        print(f"Weekend deep dive error: {e}")
        notify_error("Weekend Deep Dive", e)


def run_weekly_report():
    """일요일 정오 — Weekly Report"""
    try:
        from src.reporter.weekly import run_weekly_report as _run
        print(f"[{datetime.now()}] Starting weekly report...")
        _run()
        print(f"[{datetime.now()}] Weekly report complete!")
    except Exception as e:
        print(f"Weekly report error: {e}")
        notify_error("Weekly Report", e)


def run_server():
    """Flask 서버 + 스케줄러 동시 실행 (Railway 배포용)"""
    import threading
    from src.bot.slack import create_flask_app
    from scheduler import run_scheduler

    # 스케줄러를 백그라운드 스레드로 실행
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    print("Scheduler started in background thread")

    # Flask 서버 실행 (Slack 이벤트 수신)
    app = create_flask_app()
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [daily|weekend|weekly|server]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "daily":
        run_daily_briefing()
    elif command == "weekend":
        run_weekend_deep_dive()
    elif command == "weekly":
        run_weekly_report()
    elif command == "server":
        run_server()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
