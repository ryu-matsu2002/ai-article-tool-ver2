# app_init.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from dotenv import load_dotenv
import os

# .envの読み込み
load_dotenv()

# 拡張機能の初期化
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)

    # アプリ設定
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "devkey")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 拡張機能のアプリへの登録
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.login'  # ログインしていないときのリダイレクト先

    # ユーザーローダーの設定
    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔽 Blueprint の登録は最後に行う（循環インポート対策）
    from routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # ✅ ここを追加 → DBテーブル作成（Flaskアプリのコンテキスト内で）
    with app.app_context():
        db.create_all()

    return app
