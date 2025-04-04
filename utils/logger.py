# utils/logger.py

from models import db, Article, PostLog
from flask import current_app
from datetime import datetime
import traceback

def log_article_progress(step: str, article_id: int = None, genre: str = None, keyword: str = None, 
                         title: str = None, preview_html: str = None, tokens: int = None, cost_usd: float = None):
    """
    記事の生成・投稿ステップをログに記録し、必要に応じてArticleテーブルも更新
    """
    try:
        article = Article.query.get(article_id) if article_id else None

        # Article に情報を追記
        if article:
            if genre:
                article.genre = genre
            if preview_html:
                article.preview_html = preview_html
            if tokens is not None:
                article.gpt_tokens = tokens
            if cost_usd is not None:
                article.gpt_cost_usd = cost_usd
            article.posted_time = datetime.utcnow()
            db.session.add(article)

        # PostLog を新規作成
        log = PostLog(
            article_id=article.id if article else None,
            step=step,
            genre=genre or (article.genre if article else None),
            keyword=keyword or (article.keyword if article else None),
            title=title or (article.title if article else None),
            created_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

    except Exception as e:
        current_app.logger.error("❌ ログ記録に失敗しました:")
        current_app.logger.error(traceback.format_exc())
