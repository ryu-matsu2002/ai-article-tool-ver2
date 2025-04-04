import random
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler

from article_generator import generate_article
from models import db, Site, Article
from wordpress_client import post_to_wordpress
from utils.logger import log_article_progress

scheduler = BackgroundScheduler()

# 投稿時間帯（朝・昼・夜）
PREFERRED_HOURS = [
    (9, 11),     # 朝
    (13, 15),    # 昼
    (18, 21),    # 夜
]

def choose_random_time(start_hour, end_hour):
    hour = random.randint(start_hour, end_hour)
    minute = random.randint(0, 59)
    return time(hour, minute)

def schedule_daily_articles(app):
    """
    毎日0時に呼び出され、その日の3投稿を予約
    """
    with app.app_context():
        articles = Article.query.filter_by(status='pending').limit(3).all()
        if not articles:
            print("📭 投稿待ち記事がありません")
            return

        for i, article in enumerate(articles):
            start_hour, end_hour = PREFERRED_HOURS[i % len(PREFERRED_HOURS)]
            rand_time = choose_random_time(start_hour, end_hour)
            post_datetime = datetime.combine(datetime.today(), rand_time)

            scheduler.add_job(
                func=submit_article,
                trigger='date',
                run_date=post_datetime,
                args=[article.id, app],  # ← app を引数で渡す
                id=f"post_{article.id}"
            )

            article.scheduled_time = post_datetime
            article.status = "scheduled"
            db.session.commit()

            print(f"📅 記事ID {article.id} を {post_datetime.strftime('%Y-%m-%d %H:%M')} に予約しました")

def submit_article(article_id, app):
    """
    スケジュールされた時間に記事を投稿
    """
    with app.app_context():
        article = Article.query.get(article_id)

        if not article:
            print(f"⚠️ 記事ID {article_id} が見つかりません")
            return
        if article.status != "scheduled":
            print(f"⏸ 記事ID {article.id} はスケジュール状態ではありません（現在: {article.status}）")
            return

        site = Site.query.get(article.site_id)
        if not site:
            print(f"⚠️ サイトID {article.site_id} が見つかりません")
            return

        result = post_to_wordpress(
            title=article.title,
            content=article.content,
            site_url=site.wp_url,
            username=site.wp_username,
            app_password=site.wp_app_password,
            featured_image_url=article.featured_image_url,
            category_name="AI記事",
            publish=True
        )

        if result:
            article.status = "posted"
            article.posted_time = datetime.utcnow()
            db.session.commit()
            log_article_progress(step="投稿完了", article_id=article.id)
            print(f"✅ 記事ID {article.id} 投稿完了")
        else:
            article.status = "failed"
            db.session.commit()
            log_article_progress(step="投稿失敗", article_id=article.id)
            print(f"❌ 記事ID {article.id} 投稿失敗")

def start_scheduler(app):
    """
    スケジューラー起動設定
    """
    scheduler.start()

    # 毎日深夜0:00に投稿スケジュールを予約
    scheduler.add_job(
        func=lambda: schedule_daily_articles(app),
        trigger='cron',
        hour=0,
        minute=0
    )

    print("⏱ スケジューラーが起動しました")
