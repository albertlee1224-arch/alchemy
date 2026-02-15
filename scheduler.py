"""Alchemy Scheduler — Railway에서 cron 대신 사용"""

import schedule
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def job_daily():
    """매일 오전 06:30 (KST) Daily Briefing"""
    print(f"[{datetime.now()}] Running daily briefing...")
    try:
        from main import run_daily_briefing
        run_daily_briefing()
    except Exception as e:
        print(f"Daily briefing error: {e}")


def job_weekend():
    """토요일 오전 06:30 (KST) Weekend Deep Dive"""
    if datetime.now().weekday() == 5:  # Saturday
        print(f"[{datetime.now()}] Running weekend deep dive...")
        try:
            from main import run_weekend_deep_dive
            run_weekend_deep_dive()
        except Exception as e:
            print(f"Weekend deep dive error: {e}")


def job_weekly():
    """일요일 정오 12:00 (KST) Weekly Report"""
    if datetime.now().weekday() == 6:  # Sunday
        print(f"[{datetime.now()}] Running weekly report...")
        try:
            from main import run_weekly_report
            run_weekly_report()
        except Exception as e:
            print(f"Weekly report error: {e}")


def run_scheduler():
    """스케줄러 실행"""
    # KST = UTC+9, Railway는 UTC 기준
    # 06:30 KST = 21:30 UTC (전날)
    # 12:00 KST = 03:00 UTC
    schedule.every().day.at("21:30").do(job_daily)      # 06:30 KST
    schedule.every().day.at("21:30").do(job_weekend)     # 토 06:30 KST
    schedule.every().day.at("03:00").do(job_weekly)      # 일 12:00 KST

    print(f"[{datetime.now()}] Scheduler started!")
    print("  Daily briefing: 21:30 UTC (06:30 KST)")
    print("  Weekend deep dive: Saturday 21:30 UTC (06:30 KST)")
    print("  Weekly report: Sunday 03:00 UTC (12:00 KST)")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    run_scheduler()
