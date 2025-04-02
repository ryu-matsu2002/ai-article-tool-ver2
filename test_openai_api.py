# test_openai_api.py
from keywords import generate_keywords

genre = "筋トレ 食事"
keywords = generate_keywords(genre)

print("🔑 生成されたキーワード:")
for k in keywords:
    print("-", k)
