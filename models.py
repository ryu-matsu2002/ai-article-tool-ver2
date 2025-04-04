# models.py
from extensions import db
from flask_login import UserMixin
from datetime import datetime

# ✅ ユーザー情報（ログイン管理対象）
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    sites = db.relationship('Site', backref='user', lazy=True)
    articles = db.relationship('Article', backref='user', lazy=True)

# ✅ WordPressサイト情報
class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    site_name = db.Column(db.String(100), nullable=False)
    wp_url = db.Column(db.String(200), nullable=False)
    wp_username = db.Column(db.String(100), nullable=False)
    wp_app_password = db.Column(db.String(200), nullable=False)

    articles = db.relationship('Article', backref='site', lazy=True)

# ✅ 記事情報
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)

    keyword = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    featured_image_url = db.Column(db.String(300))

    status = db.Column(db.String(20), default="pending")  # pending, scheduled, posted, failed
    scheduled_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ 外部連携情報（例：WordPress API Token など）
class WordPressSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    site_url = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
