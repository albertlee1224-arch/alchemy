-- Alchemy Supabase Schema
-- Supabase Dashboard → SQL Editor에서 실행

-- 아티클 테이블
CREATE TABLE articles (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT,
    axis_id INTEGER,
    axis_name TEXT,
    why_new TEXT,
    new_concept_name TEXT,
    new_concept_desc TEXT,
    why_read TEXT,
    read_time TEXT,
    briefing_type TEXT DEFAULT 'daily',  -- daily, weekend
    status TEXT DEFAULT 'sent',          -- sent, starred, archived, skipped
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 뉴스 테이블
CREATE TABLE news (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT,
    hashtag TEXT,
    summary_line_1 TEXT,
    summary_line_2 TEXT,
    summary_line_3 TEXT,
    status TEXT DEFAULT 'sent',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 피드백 테이블
CREATE TABLE feedback (
    id BIGSERIAL PRIMARY KEY,
    article_url TEXT NOT NULL,
    reaction TEXT NOT NULL,  -- star, bookmark, thumbsdown
    memo TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_articles_status ON articles(status);
CREATE INDEX idx_articles_created_at ON articles(created_at);
CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_feedback_reaction ON feedback(reaction);
CREATE INDEX idx_feedback_created_at ON feedback(created_at);
