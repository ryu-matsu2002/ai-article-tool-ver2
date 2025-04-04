# utils/scheduler.py
import random
from datetime import datetime, timedelta
from models import db, Article
from utils.logger import log_article_progress

# 📅 記事10本に対してランダムな投稿時刻を設定し、status=scheduledに変更
def schedule_posting_for_articles(site_id, user_id):
    articles = Article.query.filter_by(site_id=site_id, user_id=user_id, status="pending").order_by(Article.created_at).all()

    if len(articles) < 10:
        log_article_progress(site_id, "⚠️ スケジュール投稿の対象記事が10本未満です。")
        return

    now = datetime.utcnow()
    scheduled_times = []

    # 3日間 × 3本 + 予備1本（合計10本）
    for day_offset in range(3):
        base_date = now + timedelta(days=day_offset)
        hours = random.sample(range(8, 21), 3)  # 8時〜20時からランダムに3つの時間
        for hour in sorted(hours):
            scheduled_time = base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            scheduled_times.append(scheduled_time)

    # 余った1記事は4日目の午前中に設定
    extra_time = (now + timedelta(days=3)).replace(hour=9, minute=0, second=0, microsecond=0)
    scheduled_times.append(extra_time)

    # 各記事にスケジュールを割り当て
    for article, sched_time in zip(articles, scheduled_times):
        article.scheduled_time = sched_time
        article.status = "scheduled"

    db.session.commit()

    log_article_progress(site_id, f"📅 スケジュール投稿設定完了（{len(scheduled_times)}記事分）")
