# app.py
from app_init import create_app

app = create_app()

if __name__ == "__main__":
    # ローカル環境用の起動設定
    app.run(host="0.0.0.0", port=5000, debug=True)
