# Alchemy Project

> Albert의 지적 성장을 위한 개인 큐레이션 봇.
> 매일 아침, AI가 선별한 뉴스와 아티클을 Slack으로 받는다.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | Alchemy |
| **봇 이름** | Alchemi (알케미) |
| **목적** | 매일 양질의 뉴스/아티클을 AI가 선별, 요약하여 Slack으로 전달 |
| **핵심 가치** | 지적 자극의 안정적 공급 + 취향 학습을 통한 개인화 |

---

## 2. 기술 스택

| 영역 | 기술 | 비용 |
|------|------|------|
| AI | Groq (Llama 3.3 70B) | 무료 |
| 뉴스 수집 | NewsAPI + Google News RSS | 무료 |
| 아티클 수집 | RSS 피드 (10개 소스) | 무료 |
| DB | Supabase (PostgreSQL) | 무료 |
| 봇 | Slack Bolt (Python) | 무료 |
| 서버 | Railway ($5 무료 크레딧/월) | $0 |
| 아카이브 | Notion API (Alchemy Vault) | 무료 |
| 코드 저장 | GitHub (Private) | 무료 |
| **총 비용** | | **$0/월** |

### RSS 소스 (Tier별)

**Tier 1 — 사상**: Noema Magazine, Aeon, Psyche
**Tier 2 — 분석**: MIT Technology Review, The Atlantic (Ideas), Works in Progress, Quanta Magazine
**Tier 3 — 개인 사유**: Paul Graham, Farnam Street, The Marginalian, Seth Godin

---

## 3. 5개 관심 축 (Axes)

| # | Axis | 설명 |
|---|------|------|
| 1 | Cognition & AI | 인간 인지는 어떻게 변하고 있는가 |
| 2 | Deep Work & Intellectual Craftsmanship | 깊은 사고의 기술 |
| 3 | Embodied Intelligence | 몸과 사고의 연결 |
| 4 | Philosophy of Technology | 기술 시대의 철학적 질문 |
| 5 | The New Scholar | 지식인의 역할 재정의 |

---

## 4. Slack 채널 구조

### #1_daily_briefing — 매일 06:30
- 헤더 메시지 (1개)
- 뉴스 카드 5개 (각각 개별 메시지)
- Deep Read 헤더 (1개)
- 아티클 카드 3편 (각각 개별 메시지)

### #2_weekend_read — 토요일 06:30
- 헤더 메시지 + 이번 주를 관통하는 질문 (1개)
- 주말 리딩 아티클 3편 (각각 개별 메시지)

### #3_report — 일요일 12:00
- 주간 리포트 (리딩 현황, Axis별 분포, 인상적 아티클 목록)

---

## 5. 카드 포맷

### 아티클 카드 (3-Point)

```
1️⃣ **제목**
_소스 · 읽기 시간_

🆕 왜 새로운가
[새로운 이유]

💎 새로운 개념
**개념명** — 설명

🎯 왜 읽어야 하는가
[읽어야 하는 이유]
```

### 뉴스 카드 (3줄)

```
1. #해시태그  제목
Line 1: 무슨 일이 일어났는가
Line 2: 왜 중요한가
Line 3: Albert에게 시사하는 점
🔗 기사 보기
```

---

## 6. 이모지 인터랙션

| 이모지 | 의미 | 동작 |
|--------|------|------|
| ⭐ | 인상적 | Supabase 저장 + **Notion Vault에 "⭐ 인상적"으로 아카이브** |
| 📂 | 저장 | Supabase 저장 + **Notion Vault에 "📂 저장"으로 아카이브** |
| 👎 | 관심없음 | Supabase에 status = 'skipped' 저장 + 추천 개선에 반영 |

- ⭐/📂 반응 시 Notion Vault에 자동 저장 (제목, 소스, Axis, 새로운 개념, 읽어야 하는 이유 포함)
- 👎 피드백은 `feedback` 테이블에 기록되며, 해당 토픽은 이후 추천에서 제외됨

---

## 7. DB 스키마 (Supabase)

### articles
`id`, `title`, `url`, `source`, `axis_id`, `axis_name`, `why_new`, `new_concept_name`, `new_concept_desc`, `why_read`, `read_time`, `briefing_type` (daily/weekend), `status` (sent/starred/archived/skipped), `created_at`

### news
`id`, `title`, `url`, `source`, `hashtag`, `summary_line_1`, `summary_line_2`, `summary_line_3`, `status`, `created_at`

### feedback
`id`, `article_url`, `reaction` (star/bookmark/thumbsdown), `memo`, `created_at`

---

## 8. 프로젝트 파일 구조

```
alchemy/
├── main.py                  # 메인 실행 (daily/weekend/weekly/server)
├── scheduler.py             # 스케줄러 (Railway 자동 실행)
├── requirements.txt
├── .env                     # API 키 (git 제외)
├── .gitignore
├── Procfile                 # Railway 배포용
├── railway.json
├── supabase_schema.sql      # DB 스키마
├── config/
│   ├── axes.yml             # 5개 관심축 정의
│   └── sources.yml          # RSS 소스 + 뉴스 키워드
└── src/
    ├── collector/
    │   ├── news.py           # NewsAPI + Google News RSS 수집
    │   └── articles.py       # RSS 아티클 수집
    ├── curator/
    │   ├── summarizer.py     # Groq AI 선별 + 요약
    │   └── preferences.py    # Supabase 저장 + 취향 피드백
    ├── bot/
    │   ├── slack.py          # Slack Bolt 전송 + 이벤트 수신
    │   └── formatter.py      # 메시지 포맷 (Block Kit)
    ├── vault/
    │   └── notion.py         # Notion Vault 연동 (아카이브 자동 저장)
    └── reporter/
        └── weekly.py         # 주간 리포트 + 주말 아티클 생성
```

---

## 9. 배포 환경

| 항목 | 내용 |
|------|------|
| **호스팅** | Railway (자동 배포) |
| **URL** | https://web-production-8193d2.up.railway.app |
| **GitHub** | https://github.com/albertlee1224-arch/alchemy (Private) |
| **Slack Events** | /slack/events (reaction_added 수신) |
| **Health Check** | /health |

### 스케줄 (KST 기준)
- **매일 06:30** → Daily Briefing (뉴스 5 + 아티클 3)
- **토요일 06:30** → Weekend Deep Dive (아티클 3)
- **일요일 12:00** → Weekly Report

---

## 10. 실행 방법

```bash
# Daily Briefing
python main.py daily

# Weekend Deep Dive (토요일)
python main.py weekend

# Weekly Report (일요일)
python main.py weekly

# Flask 서버 + 스케줄러 (Railway 배포용)
python main.py server
```

---

## 11. Notion Vault (Alchemy Vault)

| 속성 | 타입 | 설명 |
|------|------|------|
| Title | Title | 아티클/뉴스 제목 |
| URL | URL | 원문 링크 |
| Source | Select | 소스명 |
| Axis | Select | 5개 관심축 |
| New Concept | Text | 새로운 개념/프레임워크 |
| Concept Note | Text | 개념 설명 |
| Why It Matters | Text | 왜 읽어야 하는가 |
| Rating | Select | ⭐ 인상적 / 📂 저장 |
| Date | Date | 큐레이션 날짜 |
| Tags | Multi-select | 자유 태그 |
| My Note | Text | 읽고 난 후 메모 (수동) |

---

## 12. Phase 진행 상태

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 1 | Daily Briefing + 이모지 인터랙션 + DB 저장 | ✅ 완료 |
| Phase 2 | Notion Vault 연동 (⭐/📂 → Notion 자동 아카이브) | ✅ 완료 |
| Phase 3 | Weekend Deep Dive + Weekly Report | ✅ 완료 |
| 배포 | Railway 자동화 + Slack Event Subscription | ✅ 완료 |

---

## 13. 보안

| 항목 | 상태 |
|------|------|
| `.env` Git 제외 | ✅ `.gitignore`에 포함, 커밋 이력 없음 |
| GitHub Private 레포 | ✅ |
| Railway 환경변수 | ✅ 서버 측 암호화 저장 |
| `.env.example` | ✅ 더미 값만 포함 |

---

## 14. 향후 계획

- [ ] AI 모델 업그레이드 검토 (요약 품질 개선)
- [ ] 추천 정확도 개선 (피드백 루프 강화)
- [ ] 월간 리포트 추가 고려
- [ ] Notion Vault 활용 패턴 발전 (태그 자동화, 주간 리뷰 연동 등)

---

*마지막 업데이트: 2026.02.15*
