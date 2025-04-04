# scheduler_runner.py
from datetime import datetime
from models import db, Article, Site
from wordpress_client import post_to_wordpress
from utils.logger import log_article_progress

def run_scheduled_posts():
    now = datetime.utcnow()

    # スケジュール時刻が現在時刻以前の pending な記事を取得
    articles = Article.query.filter(
        Article.status == "scheduled",
        Article.scheduled_time <= now
    ).all()

    for article in articles:
        site = Site.query.get(article.site_id)
        if not site:
            continue

        try:
            # WordPressに投稿
            post_to_wordpress(site, article)

            # ステータス更新
            article.status = "posted"
            db.session.commit()

            log_article_progress(site.id, f"✅ 投稿完了（記事ID: {article.id}）")

        except Exception as e:
            article.status = "failed"
            db.session.commit()

            log_article_progress(site.id, f"❌ 投稿失敗（記事ID: {article.id}）: {str(e)}")

if __name__ == '__main__':
    run_scheduled_posts()
