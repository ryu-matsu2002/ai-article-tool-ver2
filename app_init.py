# app_init.py
from flask import Flask
from extensions import db, login_manager, csrf
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    # アプリ設定
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")  # PostgreSQL用のURL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 拡張機能の初期化
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.login'

    # ユーザーローダー
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ルーティング（Blueprint登録）
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # DBテーブル作成（初回のみ）
    with app.app_context():
        db.create_all()

    return app
