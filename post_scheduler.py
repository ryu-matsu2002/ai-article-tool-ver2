# post_scheduler.py
import random
from datetime import datetime, timedelta, time
from apscheduler.schedulers.background import BackgroundScheduler
from wordpress_client import post_to_wordpress
from article_generator import generate_article
from models import db, Site, Article  # Articleモデルは必要に応じて定義

scheduler = BackgroundScheduler()

# 1日の投稿時間帯（例：朝、昼、夜）
PREFERRED_HOURS = [
    (9, 11),   # 朝（9時～11時）
    (13, 15),  # 昼（13時～15時）
    (18, 21),  # 夜（18時～21時）
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

            # スケジュール実行関数を予約
            scheduler.add_job(
                func=submit_article,
                trigger='date',
                run_date=post_datetime,
                args=[article.id, app],
                id=f"post_{article.id}"
            )

            # DBにスケジュール時刻を保存（任意）
            article.scheduled_time = post_datetime
            article.status = "scheduled"
            db.session.commit()

            print(f"📅 記事ID {article.id} を {post_datetime} に予約しました")

def submit_article(article_id, app):
    """
    スケジュールされた時間に記事を投稿
    """
    with app.app_context():
        article = Article.query.get(article_id)
        site = Site.query.get(article.site_id)

        result = post_to_wordpress(
            title=article.title,
            content=article.content,
            site_url=site.wp_url,
            username=site.wp_username,
            app_password=site.wp_app_password,
            featured_image_url=article.featured_image_url,
            category_name="AI記事",  # 任意で固定 or 動的に指定
            publish=True
        )

        if result:
            article.status = "posted"
            db.session.commit()
            print(f"✅ 記事ID {article.id} 投稿完了")
        else:
            article.status = "failed"
            db.session.commit()
            print(f"❌ 記事ID {article.id} 投稿失敗")

def start_scheduler(app):
    """
    スケジューラーの起動
    """
    scheduler.start()

    # 毎日00:00に3記事の投稿予約を行う
    scheduler.add_job(
        func=lambda: schedule_daily_articles(app),
        trigger='cron',
        hour=0,
        minute=0
    )

    print("⏱ スケジューラーが起動しました")
