"""Groq 기반 아티클 요약 및 선별 모듈"""

import json
import yaml
import os
from groq import Groq
from typing import List, Dict


ALBERT_CONTEXT = """
## WHO IS ALBERT
Albert(알벗)는 AI 시대에 인간의 생각하는 힘을 극대화하는 삶을 실험하고, 그 방법을 타인에게 전달하려는 Scholar-Practitioner이다.

## BACKGROUND
- 경희대 국제학과 (UC버클리 교환, 차석졸업) → 서울대 외교학 석사 → American University 국제관계학 박사수료
- 디베이트포올 시니어강사 8년: 논증과 비판적 사고 교육 전문가
- 글쓰기 코치, 성장 파트너: Microflow 글쓰기 프로그램 운영
- 현재 이직 탐색 중, 10년 후 목표는 Scholar-Practitioner (기업 강의, 명상 기반 생산성 지도, 글쓰기+통찰 프로그램)

## DAILY PRACTICE
- 매일 Hatha Yoga, 단전호흡(현재 24초-24초, 목표 태식 2분-2분), 명상 수행
- 기감 형성됨, 1년+ 수행 지속
- 요명차: 요가·명상·차·글쓰기를 결합한 개인 루틴

## CORE BELIEFS
- AI는 단순 생산성 도구가 아니라 "인지 확장 장치"
- 꽂히는 것이 아니면 집중 어려움 → 의미 연결 패턴으로 작동하는 사람
- 성공보다 "의식적 진화"가 삶의 중심축
- 영향을 준 인물: 이나모리 가즈오, 야마구치 슈, 나발 라비칸트, Chris Williamson, Dan Koe (공통점: 깊은 사유와 실행을 연결시킨 사람들)

## WHAT ALBERT NEEDS FROM THIS CURATION
- 빠르게 변화하는 트렌드의 철학적/사상적/패러다임적 의미를 파악하고 싶다
- 새로운 개념, 프레임워크, 패러다임을 접하고 싶다
- 강의와 코칭에서 활용할 수 있는 지적 자산을 쌓고 싶다
- 자신의 수행(요가/호흡/명상)에 과학적 근거와 지적 프레임을 연결하고 싶다
- "일하는 사람의 성장을 돕는" 커리어 미션에 영감을 줄 콘텐츠가 필요하다

## TONE GUIDE
- Generic하거나 뻔한 요약은 절대 하지 말 것
- Albert의 구체적 상황과 연결된 "So What"을 제시할 것
- 새로운 용어나 개념이 있으면 반드시 짚어줄 것
- 한국어 요약은 자연스럽고 밀도 높게, 불필요한 수식어 제거
"""


ARTICLE_EXAMPLE = """
## GOOD EXAMPLE (3-Point Card)

Title: "The Case Against Cognitive Outsourcing"
Source: Noema Magazine

🆕 왜 새로운가
AI에게 사고를 위임하는 것이 "인지 확장"이 아니라 "인지 위축"이라는 반론이 본격 등장. Extended Mind 이론에 대한 체계적 반박.

💎 새로운 개념
Cognitive Atrophy (인지 위축) — 사용하지 않는 인지 능력은 근육처럼 퇴화한다는 프레임워크. AI 의존도가 높아질수록 메타인지 능력이 약화된다는 주장.

🎯 왜 읽어야 하는가
AI를 인지 확장 장치로 쓰는 Albert의 전제를 정면으로 도전하는 글. 반론을 알아야 자기 입장이 단단해진다. 코칭/강의에서 "AI를 어떻게 써야 하는가" 논의의 핵심 레퍼런스.

## BAD EXAMPLE (too generic, avoid this)
🆕 왜 새로운가: AI와 인지에 대한 새로운 관점을 제시합니다.
💎 새로운 개념: 인지 위축이라는 개념이 소개됩니다.
🎯 왜 읽어야 하는가: AI 시대에 중요한 주제입니다.
"""


def load_axes(config_path: str = None) -> List[Dict]:
    """Axes 설정 로드"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "config", "axes.yml"
        )
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("axes", [])


def init_model(api_key: str):
    """Groq 클라이언트 초기화"""
    return Groq(api_key=api_key)


def _call_groq(client, prompt: str) -> str:
    """Groq API 호출 공통 함수"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content.strip()


def select_and_summarize_news(client, news_articles: List[Dict], count: int = 5) -> List[Dict]:
    """뉴스 중 가장 관련성 높은 것을 선별하고 3줄 요약"""

    axes_info = load_axes()
    axes_text = "\n".join([f"- Axis {a['id']}: {a['name']} — {a['description']}" for a in axes_info])

    news_list = "\n\n".join([
        f"[{i+1}] {n['title']}\nSource: {n['source']}\nURL: {n['url']}\nDescription: {n['description'][:300]}"
        for i, n in enumerate(news_articles[:30])
    ])

    prompt = f"""You are Alchemi, Albert's personal news curator. You deeply understand Albert and curate news specifically for him.

{ALBERT_CONTEXT}

The 5 Axes of interest:
{axes_text}

TASK: Select the {count} most relevant news for Albert. Be highly selective — only news that intersects with Albert's specific interests above.

For each selected news, provide:
1. A hashtag keyword in Korean (e.g., #AI정책, #인지과학, #명상연구, #교육혁신, #생산성과학)
2. The original title
3. Exactly 3 lines of summary in Korean:
   - Line 1: 무슨 일이 일어났는가 (사실)
   - Line 2: 왜 중요한가 (맥락/의미)
   - Line 3: Albert에게 시사하는 점 (개인화된 인사이트)
4. The original URL

IMPORTANT:
- 3번째 줄은 반드시 Albert의 구체적 상황(수행, 코칭, 강의, AI 활용 등)과 연결할 것
- 뻔하거나 generic한 요약은 하지 말 것. 밀도 높고 구체적으로.

NEWS ARTICLES:
{news_list}

Respond in JSON format:
{{
  "selected_news": [
    {{
      "hashtag": "#키워드",
      "title": "headline",
      "summary_line_1": "무슨 일이 일어났는가",
      "summary_line_2": "왜 중요한가",
      "summary_line_3": "Albert에게 시사하는 점",
      "url": "https://...",
      "source": "source name"
    }}
  ]
}}

Select exactly {count} articles. All summaries MUST be in Korean. Be specific, not generic."""

    try:
        text = _call_groq(client, prompt)
        result = json.loads(text)
        return result.get("selected_news", [])
    except Exception as e:
        print(f"News summarization error: {e}")
        return []


def select_and_summarize_articles(
    client, articles: List[Dict], count: int = 3, excluded_topics: List[str] = None
) -> List[Dict]:
    """아티클 중 Deep Read 3편을 선별하고 3-Point 카드 생성"""

    axes_info = load_axes()
    axes_text = "\n".join([f"- Axis {a['id']}: {a['name']} — {a['description']}" for a in axes_info])

    exclusion_note = ""
    if excluded_topics:
        exclusion_note = f"\n\nEXCLUDED TOPICS (user marked as not interested): {', '.join(excluded_topics)}"

    articles_list = "\n\n".join([
        f"[{i+1}] {a['title']}\nSource: {a['source']} (Tier {a.get('tier', 3)})\nURL: {a['url']}\nPreview: {a.get('content_preview', '')[:500]}"
        for i, a in enumerate(articles[:25])
    ])

    prompt = f"""You are Alchemi, Albert's Deep Read curator. You know Albert deeply and select articles that will genuinely expand his thinking.

{ALBERT_CONTEXT}

{ARTICLE_EXAMPLE}

The 5 Axes:
{axes_text}

Article Selection Criteria:
- Timeless over Timely: perspectives valid 10 years from now
- Argument over Information: articles with clear thesis and reasoning, not just reporting
- Paradigm-shifting: introduces new concepts, frameworks, or challenges existing mental models
- Prioritize Tier 1 sources (Aeon, Noema, Psyche), then Tier 2, then Tier 3
{exclusion_note}

TASK: Select the {count} best Deep Read picks and create a 3-Point Card for each.

CRITICAL RULES for each card:
- 🆕 왜 새로운가: What is genuinely NEW about this article's argument? Not a vague summary. What specific claim or evidence is fresh?
- 💎 새로운 개념: Name ONE specific concept/framework/term from the article. If the article doesn't introduce one, extract the implicit framework and name it.
- 🎯 왜 읽어야 하는가: Connect DIRECTLY to Albert's specific situation — his breathing practice (24초), his debate coaching background, his AI-as-cognitive-extension philosophy, his goal of becoming a Scholar-Practitioner. Be SPECIFIC, not generic.

Follow the GOOD EXAMPLE above. Avoid the BAD EXAMPLE patterns.

ARTICLES:
{articles_list}

Respond in JSON format:
{{
  "selected_articles": [
    {{
      "title": "article title",
      "source": "source name",
      "url": "https://...",
      "read_time": "12 min",
      "axis_id": 1,
      "axis_name": "Cognition & AI",
      "why_new": "왜 새로운가 (구체적으로, 2문장)",
      "new_concept_name": "개념/프레임워크 이름 (영문)",
      "new_concept_desc": "개념 설명 (1문장, 한국어)",
      "why_read": "왜 읽어야 하는가 (Albert의 구체적 상황과 연결, 2문장)"
    }}
  ]
}}

Select exactly {count} articles. Cover different Axes. All Korean descriptions must be dense, specific, and avoid filler words."""

    try:
        text = _call_groq(client, prompt)
        result = json.loads(text)
        return result.get("selected_articles", [])
    except Exception as e:
        print(f"Article summarization error: {e}")
        return []
