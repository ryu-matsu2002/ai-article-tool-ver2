# article_generator.py
import openai
import os
import requests
from dotenv import load_dotenv

# .envの読み込み
load_dotenv()

# OpenAIとPixabayのAPIキー設定
openai.api_key = os.getenv("OPENAI_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")


def generate_title_from_keyword(keyword):
    """
    入力キーワードに基づいて、Q&A形式のSEO記事タイトルを1つ生成
    """
    prompt = f"""
あなたはSEOとコンテンツマーケティングの専門家です。

入力されたキーワードを使って
WEBサイトのQ＆A記事コンテンツに使用する「記事タイトル」を10個考えてください。

記事タイトルには必ず入力されたキーワードを全て使ってください。
キーワードの順番は入れ替えないでください。
最後は「？」で締めてください。

キーワード: {keyword}
出力形式: 箇条書き
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはSEOに強いプロのライターです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        output = response.choices[0].message.content
        lines = [line.strip("-・●●0123456789. ").strip() for line in output.strip().split("\n") if line.strip()]
        return lines[0] if lines else f"{keyword} に関するQ&A記事"

    except Exception as e:
        print("タイトル生成エラー:", e)
        return f"{keyword} に関するQ&A記事"


def generate_article_body(title):
    """
    タイトルに対してQ&A形式のSEO記事本文を生成（2500〜3500文字程度）
    """
    prompt = f"""
あなたはSEOとコンテンツマーケティングの専門家です。

入力された「Q＆A記事のタイトル」に対しての
回答記事を以下の###条件###に沿って書いてください。

タイトル: 「{title}」

###条件###

・文章の構成としては、問題提起、共感、問題解決策を入れて書いてください。
・Q＆A記事のタイトルについて悩んでいる人が知りたい事を書いてください。
・見出し（hタグ）を付けてわかりやすく書いてください
・記事の文字数は必ず2000文字程度でまとめてください
・1行の長さは30文字前後にして接続詞などで改行してください。
・「文章の島」は1行から3行以内にして、文章の島同士は2行空けてください
・親友に向けて話すように書いてください（ただし敬語を使ってください）
・読み手のことは「皆さん」ではなく必ず「あなた」と書いてください。
"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはSEOに強いプロの日本語ライターです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("本文生成エラー:", e)
        return "本文生成に失敗しました。"


def get_pixabay_images(keyword, num_images=2):
    """
    Pixabayから画像URLを取得
    """
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": num_images,
        "safesearch": "true",
        "lang": "ja"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        hits = data.get("hits", [])
        return [hit["webformatURL"] for hit in hits][:num_images]

    except Exception as e:
        print("Pixabay画像取得エラー:", e)
        return []


def generate_article(keyword):
    """
    キーワードから記事一式を生成（タイトル＋本文＋画像）
    """
    title = generate_title_from_keyword(keyword)
    content = generate_article_body(title)
    image_keyword = keyword  # ここでは入力キーワードを画像検索用にも使う
    images = get_pixabay_images(image_keyword)

    return {
        "title": title,
        "content": content,
        "image_keyword": image_keyword,
        "featured_image_url": images[0] if len(images) > 0 else "",
        "content_image_url": images[1] if len(images) > 1 else ""
    }
