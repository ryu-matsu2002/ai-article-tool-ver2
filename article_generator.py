# article_generator.py

import openai
import os
import requests
import time
from dotenv import load_dotenv
from .utils.logger import log_article_progress


# .envの読み込み
load_dotenv()

# APIキー
openai.api_key = os.getenv("OPENAI_API_KEY")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")

# APIコスト計算用（GPT-4）
GPT4_INPUT_COST = 0.01 / 1000  # $0.01 / 1K tokens
GPT4_OUTPUT_COST = 0.03 / 1000  # $0.03 / 1K tokens


def generate_title_from_keyword(keyword):
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
            max_tokens=500  # ✅ タイトルは短く済むので変更なし
        )

        output = response.choices[0].message.content
        lines = [line.strip("-・●●0123456789. ").strip() for line in output.strip().split("\n") if line.strip()]
        return lines[0] if lines else f"{keyword} に関するQ&A記事"

    except Exception as e:
        print("タイトル生成エラー:", e)
        return f"{keyword} に関するQ&A記事"


def generate_article_body(title):
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
            max_tokens=2000  # ✅ コスト削減＆タイムアウト対策
        )

        usage = response.usage
        content = response.choices[0].message.content.strip()

        return {
            "body": content,
            "input_tokens": usage.prompt_tokens,
            "output_tokens": usage.completion_tokens
        }

    except Exception as e:
        print("本文生成エラー:", e)
        return {
            "body": "本文生成に失敗しました。",
            "input_tokens": 0,
            "output_tokens": 0
        }


def get_pixabay_images(keyword, num_images=2):
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


def generate_article(keyword, genre=None, user_id=None, site_id=None):
    """
    キーワードから記事一式を生成（タイトル＋本文＋画像＋ログ記録＋インターバル付き）
    """
    time.sleep(3)  # インターバル①：キーワードごとに待機

    title = generate_title_from_keyword(keyword)
    time.sleep(3)  # インターバル②：タイトル生成後に待機

    article_data = generate_article_body(title)
    content = article_data["body"]
    input_tokens = article_data["input_tokens"]
    output_tokens = article_data["output_tokens"]
    gpt_cost = input_tokens * GPT4_INPUT_COST + output_tokens * GPT4_OUTPUT_COST

    images = get_pixabay_images(keyword)
    featured_image = images[0] if len(images) > 0 else ""
    content_image = images[1] if len(images) > 1 else ""

    # ✅ プレビューHTML作成
    preview_html = f"<h2>{title}</h2>\n<img src='{featured_image}' style='max-width:100%;'>\n<p>{content[:300]}...</p>"

    # ✅ ログ記録
    log_article_progress(
        step="記事生成完了",
        genre=genre,
        keyword=keyword,
        title=title,
        preview_html=preview_html,
        gpt_tokens=input_tokens + output_tokens,
        gpt_cost_usd=gpt_cost,
        user_id=user_id,
        site_id=site_id
    )

    return {
        "title": title,
        "content": content,
        "image_keyword": keyword,
        "featured_image_url": featured_image,
        "content_image_url": content_image,
        "gpt_tokens": input_tokens + output_tokens,
        "gpt_cost_usd": gpt_cost
    }
