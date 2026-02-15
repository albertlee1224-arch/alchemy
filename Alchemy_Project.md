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
| AI | Groq (Llama 3.3 70B) — 3-에이전트 시스템 | 무료 |
| 뉴스 수집 | NewsAPI + Google News RSS | 무료 |
| 아티클 수집 | RSS 피드 (11개 소스) | 무료 |
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

## 3. 3-에이전트 큐레이션 시스템

아티클 큐레이션에 3개의 전문 에이전트가 순차 작동:

| Agent | 역할 | 집중 영역 |
|-------|------|-----------|
| **Selector** | 25개 → 3개 선별 | Axis 다양성, Tier 우선순위, 패러다임 전환 여부 |
| **Analyst** | 3-Point Card 작성 | 왜 새로운가 / 새로운 개념 / 왜 읽어야 하는가 |
| **Connector** | 아티클 간 연결 발견 | "오늘의 브리핑을 관통하는 질문" 생성 + ⭐ 이력 참조 |

```
RSS 수집 → [Selector: 선별] → [Analyst: 분석] → [Connector: 연결] → Slack 전송
```

뉴스는 단일 에이전트 (가벼운 토막뉴스이므로 1회 호출로 충분)

---

## 4. 5개 관심 축 (Axes)

| # | Axis | 설명 |
|---|------|------|
| 1 | Cognition & AI | 인간 인지는 어떻게 변하고 있는가 |
| 2 | Deep Work & Intellectual Craftsmanship | 깊은 사고의 기술 |
| 3 | Embodied Intelligence | 몸과 사고의 연결 |
| 4 | Philosophy of Technology | 기술 시대의 철학적 질문 |
| 5 | The New Scholar | 지식인의 역할 재정의 |

---

## 5. Slack 채널 구조

### #1_daily_briefing — 매일 06:30
- 헤더 메시지 (1개)
- 뉴스 카드 5개 (각각 개별 메시지)
- Deep Read 헤더 + 🔗 관통하는 질문 (1개)
- 아티클 카드 3편 (각각 개별 메시지)

### #2_weekend_read — 토요일 06:30
- 헤더 메시지 + 이번 주를 관통하는 질문 (1개)
- 주말 리딩 아티클 3편 (각각 개별 메시지)

### #3_report — 일요일 12:00
- 주간 리포트 (리딩 현황, Axis별 분포, 인상적 아티클 목록)

---

## 6. 카드 포맷

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

## 7. 이모지 인터랙션

| 이모지 | 의미 | 동작 |
|--------|------|------|
| ⭐ | 인상적 | Supabase 저장 + **Notion Vault에 "⭐ 인상적"으로 아카이브** |
| 📂 | 저장 | Supabase 저장 + **Notion Vault에 "📂 저장"으로 아카이브** |
| 👎 | 관심없음 | Supabase에 status = 'skipped' 저장 + 추천 개선에 반영 |

- ⭐/📂 반응 시 Notion Vault에 자동 저장 (제목, 소스, Axis, 새로운 개념, 읽어야 하는 이유 포함)
- 👎 피드백은 `feedback` 테이블에 기록되며, 해당 토픽은 이후 추천에서 제외됨
- ⭐ 이력은 Connector 에이전트가 참조하여 개인화 강화

---

## 8. 안전장치

- **에러 알림**: Daily/Weekend/Weekly 실행 실패 시 Slack `#1_daily_briefing`에 에러 메시지 자동 전송
- **중복 방지**: 최근 7일 내 추천된 URL은 자동 제외
- **👎 피드백**: 3회 이상 thumbsdown 받은 Axis/Source는 추천에서 제외

---

## 9. DB 스키마 (Supabase)

### articles
`id`, `title`, `url`, `source`, `axis_id`, `axis_name`, `why_new`, `new_concept_name`, `new_concept_desc`, `why_read`, `read_time`, `briefing_type` (daily/weekend), `status` (sent/starred/archived/skipped), `created_at`

### news
`id`, `title`, `url`, `source`, `hashtag`, `summary_line_1`, `summary_line_2`, `summary_line_3`, `status`, `created_at`

### feedback
`id`, `article_url`, `reaction` (star/bookmark/thumbsdown), `memo`, `created_at`

---

## 10. Notion Vault (Alchemy Vault)

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

## 11. 프로젝트 파일 구조

```
alchemy/
├── main.py                  # 메인 실행 (daily/weekend/weekly/server)
├── scheduler.py             # 스케줄러 (Railway 자동 실행)
├── requirements.txt
├── .env                     # API 키 (git 제외)
├── .env.example             # 환경변수 템플릿
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
    │   ├── summarizer.py     # 3-에이전트 큐레이션 (Selector→Analyst→Connector)
    │   └── preferences.py    # Supabase 저장 + 취향 피드백 + 중복 방지
    ├── bot/
    │   ├── slack.py          # Slack Bolt 전송 + 이벤트 수신 + Notion 연동
    │   └── formatter.py      # 메시지 포맷 (Block Kit)
    ├── vault/
    │   └── notion.py         # Notion Vault 연동 (아카이브 자동 저장)
    └── reporter/
        └── weekly.py         # 주간 리포트 + 주말 아티클 생성
```

---

## 12. 배포 환경

| 항목 | 내용 |
|------|------|
| **호스팅** | Railway (GitHub 연동 자동 배포) |
| **URL** | https://web-production-8193d2.up.railway.app |
| **GitHub** | https://github.com/albertlee1224-arch/alchemy (Private) |
| **Slack Events** | /slack/events (reaction_added 수신) |
| **Health Check** | /health |

### 스케줄 (KST 기준)
- **매일 06:30** → Daily Briefing (뉴스 5 + 아티클 3 + 관통하는 질문)
- **토요일 06:30** → Weekend Deep Dive (아티클 3 + 주간 연결고리)
- **일요일 12:00** → Weekly Report

---

## 13. 보안

| 항목 | 상태 |
|------|------|
| `.env` Git 제외 | ✅ `.gitignore`에 포함, 커밋 이력 없음 |
| GitHub Private 레포 | ✅ |
| Railway 환경변수 | ✅ 서버 측 암호화 저장 |
| `.env.example` | ✅ 더미 값만 포함 |

---

## 14. Phase 진행 상태

| Phase | 내용 | 상태 |
|-------|------|------|
| Phase 1 | Daily Briefing + 이모지 인터랙션 + DB 저장 | ✅ 완료 |
| Phase 2 | Notion Vault 연동 (⭐/📂 → Notion 자동 아카이브) | ✅ 완료 |
| Phase 3 | Weekend Deep Dive + Weekly Report | ✅ 완료 |
| Phase 4 | 3-에이전트 큐레이션 시스템 | ✅ 완료 |
| 배포 | Railway 자동화 + Slack Event Subscription | ✅ 완료 |

---

## 15. 미해결 / 향후 계획

### 확인 필요
- [ ] Slack 이모지 반응 → Supabase + Notion 저장 (Railway 라이브 검증)
- [ ] Slack Event Subscription 권한 확인 (`reactions:read`, `channels:history`)

### 1주 후 판단
- [ ] 06:30 타이밍 적절한지 (실제 사용 패턴 확인)
- [ ] 뉴스 5 + 아티클 3 양이 적절한지
- [ ] AI 요약 품질 체감 평가
- [ ] 이모지 사용 패턴 분석

### 향후 개선
- [ ] AI 모델 업그레이드 검토 (GPT-4o-mini ~$1-3/월)
- [ ] 소스 확장 (명상/신체지성 분야)
- [ ] Weekly Report에 성공 지표 포함
- [ ] "이번 주 수집된 개념 목록" 리포트 추가
- [ ] Notion Vault 활용 패턴 발전 (태그 자동화, 주간 리뷰 연동)

---

*마지막 업데이트: 2026.02.15*
