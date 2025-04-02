# wordpress_client.py
import requests
from requests.auth import HTTPBasicAuth

def upload_featured_image(site_url, username, app_password, image_url):
    """
    画像URLをダウンロードし、WordPressメディアにアップロード → メディアIDを返す
    """
    try:
        # 画像をダウンロード
        image_data = requests.get(image_url).content
        filename = image_url.split("/")[-1]

        # WordPress メディアAPIへアップロード
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "image/jpeg"
        }
        media_url = f"{site_url}/wp-json/wp/v2/media"

        response = requests.post(
            media_url,
            headers=headers,
            data=image_data,
            auth=HTTPBasicAuth(username, app_password)
        )

        if response.status_code in [200, 201]:
            media_id = response.json()["id"]
            print(f"🖼 画像アップロード成功: media_id={media_id}")
            return media_id
        else:
            print("❌ 画像アップロード失敗:", response.status_code, response.text)
            return None

    except Exception as e:
        print("⚠️ 画像アップロードエラー:", e)
        return None


def get_or_create_category(site_url, username, app_password, category_name):
    """
    カテゴリがあればIDを取得、なければ新規作成してIDを返す
    """
    try:
        # 一致するカテゴリ検索
        url = f"{site_url}/wp-json/wp/v2/categories"
        params = {"search": category_name}
        response = requests.get(url, auth=HTTPBasicAuth(username, app_password), params=params)

        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]["id"]

        # なければ新規作成
        response = requests.post(
            url,
            auth=HTTPBasicAuth(username, app_password),
            json={"name": category_name}
        )
        if response.status_code in [200, 201]:
            return response.json()["id"]
    except:
        pass
    return None


def post_to_wordpress(title, content, site_url, username, app_password,
                      featured_image_url=None, category_name=None, tags=None, publish=True):
    """
    WordPressへ記事投稿＋アイキャッチ画像＋カテゴリ・タグ指定＋失敗時ログ
    """
    try:
        # アイキャッチ画像をWordPressへアップロード（必要なら）
        featured_media_id = None
        if featured_image_url:
            featured_media_id = upload_featured_image(site_url, username, app_password, featured_image_url)

        # カテゴリID取得
        category_id = None
        if category_name:
            category_id = get_or_create_category(site_url, username, app_password, category_name)

        # タグ（文字列→タグ名配列）※要対応なら後ほど

        post_data = {
            "title": title,
            "content": content,
            "status": "publish" if publish else "draft",
        }

        if featured_media_id:
            post_data["featured_media"] = featured_media_id
        if category_id:
            post_data["categories"] = [category_id]
        if tags:
            post_data["tags"] = tags

        # 投稿実行
        response = requests.post(
            f"{site_url}/wp-json/wp/v2/posts",
            auth=HTTPBasicAuth(username, app_password),
            json=post_data
        )

        if response.status_code in [200, 201]:
            print("✅ 投稿成功:", response.json().get("id"))
            return response.json()
        else:
            print("❌ 投稿失敗:", response.status_code)
            print(response.text)
            # 🔽 投稿失敗ログ保存などここで対応可
            return None

    except Exception as e:
        print("⚠️ 投稿中エラー:", e)
        return None
