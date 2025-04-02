# init_db.py
from app_init import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ データベースを作成しました。")
