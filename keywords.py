# keywords.py（OpenAI v1.0以上対応版）
import openai
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_keywords(genre):
    prompt = f"""
あなたはSEOマーケティングの専門家です。
以下のジャンルに対して、検索上位を狙える【3語以上のロングテールキーワード】を10個、日本語で出力してください。

ジャンル: {genre}

条件:
- ３語以上のロングテールキーワード
- 必ず10個
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたはSEOに特化したマーケターです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content
        keywords = [line.replace("・", "").strip("-・●●0123456789. ").strip()
                    for line in content.strip().split("\n") if line.strip()]
        return keywords[:10]

    except Exception as e:
        print("キーワード生成中にエラーが発生しました:", e)
        return []
