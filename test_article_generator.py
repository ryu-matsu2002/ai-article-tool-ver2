# test_article_generator.py
from article_generator import generate_article

keyword = "筋トレ後のおすすめ食事"
result = generate_article(keyword)

if result:
    print("📌 タイトル:", result["title"])
    print("📝 本文:\n", result["content"])
    print("🖼 画像キーワード:", result["image_keyword"])
else:
    print("記事の生成に失敗しました。")
