# utils/async_article_generator.py
import time
import random
from datetime import datetime
from openai import OpenAI

from models import db, Article
from utils.logger import log_article_progress
from prompts import get_keyword_prompt, get_article_prompt
from utils.scheduler import schedule_posting_for_articles

# OpenAI API 初期化
client = OpenAI()

# 🔸 記事生成メイン処理

def generate_articles_safely(genre, site_id, user_id, sleep_interval=10):
    # Step 1: キーワード10個生成
    keyword_prompt = get_keyword_prompt(genre)
    log_article_progress(site_id, "🧠 キーワードを生成中…")

    try:
        keyword_response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": keyword_prompt}],
            max_tokens=500,
            temperature=0.7
        )
        keywords_text = keyword_response.choices[0].message.content.strip()
        keywords = [kw.strip() for kw in keywords_text.split('\n') if kw.strip()]
    except Exception as e:
        log_article_progress(site_id, f"❌ キーワード生成エラー: {str(e)}")
        return

    log_article_progress(site_id, f"📝 キーワード生成完了：{len(keywords)}件")

    # Step 2: 各キーワードごとに記事生成
    for i, keyword in enumerate(keywords):
        log_article_progress(site_id, f"📝 記事{i+1}（{keyword}）生成中…")

        # インターバル（安全対策）
        time.sleep(sleep_interval)

        article_prompt = get_article_prompt(genre, keyword)
        try:
            article_response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": article_prompt}],
                max_tokens=1000,  # ← max_tokens 節約
                temperature=0.7
            )
            content = article_response.choices[0].message.content.strip()
            title = keyword  # キーワードを仮タイトルとする

            article = Article(
                user_id=user_id,
                site_id=site_id,
                title=title,
                content=content,
                keyword=keyword,
                status="pending",
                created_at=datetime.utcnow()
            )
            db.session.add(article)
            db.session.commit()

            log_article_progress(site_id, f"✅ 記事{i+1}（{keyword}）生成完了")

        except Exception as e:
            log_article_progress(site_id, f"❌ 記事{i+1} エラー: {str(e)}")
            continue

    # Step 3: すべて完了後、スケジュール投稿へ移行
    log_article_progress(site_id, "✅ 10記事すべて生成完了。スケジュール投稿を開始します。")
    try:
        schedule_posting_for_articles(site_id, user_id)
    except Exception as e:
        log_article_progress(site_id, f"❌ スケジュール投稿設定エラー: {str(e)}")
