from flask import Flask
from extensions import db
import os
from dotenv import load_dotenv
from sqlalchemy import text  # ✅ 追加！

# .envから読み込み
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))  # ✅ text() で囲む
    db.session.commit()
    print("✅ alembic_version テーブルを削除しました。")
