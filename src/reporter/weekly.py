"""주간 리포트 및 Weekly Connection 생성"""

import json
import os
from typing import List, Dict

from src.curator.preferences import get_supabase_client, get_weekly_stats
from src.curator.summarizer import ALBERT_CONTEXT, _call_groq


def generate_weekly_connection(client, starred_articles: List[Dict]) -> str:
    """이번 주 ⭐ 아티클을 관통하는 질문 생성"""
    if not starred_articles:
        return "이번 주는 어떤 생각이 알벗의 마음을 움직였나요?"

    articles_text = "\n".join([
        f"- {a.get('title', '')} (Axis: {a.get('axis_name', '')})"
        for a in starred_articles
    ])

    prompt = f"""You are ALBOT, Albert's intellectual companion.

{ALBERT_CONTEXT}

This week, Albert starred these articles as impressive:
{articles_text}

Generate ONE powerful question in Korean that connects these articles into a single thread of inquiry.
The question should:
- Be thought-provoking and personal to Albert
- Connect at least 2 of the articles thematically
- Be suitable as "이번 주를 관통하는 질문"

Respond in JSON format:
{{"question": "질문 내용"}}"""

    try:
        text = _call_groq(client, prompt)
        result = json.loads(text)
        return result.get("question", "이번 주 읽은 글들은 알벗에게 어떤 새로운 질문을 던졌는가?")
    except Exception as e:
        print(f"Weekly connection error: {e}")
        return "이번 주 읽은 글들은 알벗에게 어떤 새로운 질문을 던졌는가?"


def generate_weekend_articles(client, articles: List[Dict], count: int = 3) -> List[Dict]:
    """주말 Deep Dive용 아티클 선별 (Long Read 중심)"""
    from src.curator.summarizer import select_and_summarize_articles
    return select_and_summarize_articles(client, articles, count=count)


def run_weekly_report():
    """주간 리포트 실행"""
    from src.bot.slack import send_weekly_report

    supabase = get_supabase_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )

    stats = get_weekly_stats(supabase)
    send_weekly_report(stats)
    print("Weekly report sent!")
