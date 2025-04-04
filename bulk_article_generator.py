# bulk_article_generator.py

import time
from datetime import datetime

from keywords import generate_keywords
from article_generator import generate_article
from models import Article, db
from utils.logger import log_article_progress


def generate_bulk_articles(genre, site_id, user_id):
    """
    指定ジャンルから10記事を自動生成し、DBに保存（pending）状態。
    各処理間に十分なインターバルを挟み、負荷を分散して確実に完了させる。
    """

    print(f"🎯 ジャンル: {genre} で記事生成を開始します")

    # ✅ ステップ1：キーワード生成
    keywords = generate_keywords(genre)
    print(f"🔑 {len(keywords)} 個のキーワードを取得しました")

    log_article_progress(
        step="キーワード取得完了",
        genre=genre,
        keyword=", ".join(keywords)
    )

    # 🔁 キーワード取得後、待機（API連続防止）
    time.sleep(5)

    # ✅ ステップ2：記事生成
    for i, keyword in enumerate(keywords):
        print(f"📝 記事 {i + 1} / {len(keywords)} を生成中... keyword: {keyword}")

        # 🔄 生成中フラグでDBに仮登録（status="generating"）
        article = Article(
            site_id=site_id,
            user_id=user_id,
            keyword=keyword,
            title="タイトル生成中...",
            content="本文生成中...",
            featured_image_url="",
            status="generating",
            created_at=datetime.utcnow(),
            genre=genre
        )
        db.session.add(article)
        db.session.commit()

        # ⏱️ タイトル生成前にインターバル
        time.sleep(5)

        # ✅ 本文・画像含む記事データを生成
        article_data = generate_article(
            keyword=keyword,
            genre=genre,
            user_id=user_id,
            site_id=site_id
        )

        # ⏱️ 本文生成後の追加待機（画像取得含む）
        time.sleep(5)

        if article_data:
            # 🔁 仮登録した記事を更新
            article.title = article_data["title"]
            article.content = article_data["content"]
            article.featured_image_url = article_data["featured_image_url"]
            article.preview_html = f"<h2>{article_data['title']}</h2><p>{article_data['content'][:300]}...</p>"
            article.gpt_tokens = article_data.get("gpt_tokens")
            article.gpt_cost_usd = article_data.get("gpt_cost_usd")
            article.status = "pending"
            db.session.commit()

            print(f"✅ 記事 {i + 1} 保存完了")

            log_article_progress(
                step="記事生成完了",
                article_id=article.id,
                genre=genre,
                keyword=keyword,
                title=article.title,
                preview_html=article.preview_html,
                tokens=article.gpt_tokens,
                cost_usd=article.gpt_cost_usd
            )

        else:
            print(f"❌ 記事 {i + 1} の生成に失敗しました")
            article.status = "failed"
            db.session.commit()

        # ⏱️ 各記事生成間のインターバル（確実な分散）
        time.sleep(5)

    print("🎉 全記事の生成が完了しました")
