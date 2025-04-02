# bulk_article_generator.py
from keywords import generate_keywords
from article_generator import generate_article
from models import Article, db
from datetime import datetime

def generate_bulk_articles(genre, site_id, user_id):
    """
    指定ジャンルから10記事を自動生成し、DBに保存（pending）
    - site_id: 投稿先のWordPressサイトID
    - user_id: 現在ログインしているユーザーID
    """
    keywords = generate_keywords(genre)
    print(f"🔑 {len(keywords)}個のキーワードを取得しました")

    for i, keyword in enumerate(keywords):
        print(f"📝 記事 {i+1} / 10 を生成中... keyword: {keyword}")
        article_data = generate_article(keyword)

        if article_data:
            article = Article(
                site_id=site_id,
                user_id=user_id,
                keyword=keyword,
                title=article_data["title"],
                content=article_data["content"],
                featured_image_url=article_data["featured_image_url"],
                status="pending",
                created_at=datetime.utcnow()
            )
            db.session.add(article)
            db.session.commit()
            print(f"✅ 記事 {i+1} 保存完了")
        else:
            print(f"❌ 記事 {i+1} 生成に失敗しました")
