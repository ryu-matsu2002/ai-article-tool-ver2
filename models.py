from extensions import db
from flask_login import UserMixin
from datetime import datetime

# ✅ ユーザー情報（ログイン管理対象）
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

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
    logs = db.relationship('PostLog', backref='site', lazy=True)

# ✅ 記事情報（生成・編集・投稿管理）
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)

    genre = db.Column(db.String(100))
    keyword = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    preview_html = db.Column(db.Text)
    featured_image_url = db.Column(db.String(300))

    status = db.Column(db.String(20), default="draft")  # draft, scheduled, posted, error
    scheduled_time = db.Column(db.DateTime)
    posted_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    gpt_tokens = db.Column(db.Integer)
    gpt_cost_usd = db.Column(db.Float)

# ✅ 投稿ログ（記事単位、詳細ステップ記録用）
class PostLog(db.Model):
    __tablename__ = "post_log"
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"))
    site_id = db.Column(db.Integer, db.ForeignKey("site.id"))
    step = db.Column(db.String(100))  # 例: "キーワード取得", "記事生成完了"
    genre = db.Column(db.String(100))
    keyword = db.Column(db.String(255))
    title = db.Column(db.String(300))
    preview_html = db.Column(db.Text)
    gpt_tokens = db.Column(db.Integer)
    gpt_cost_usd = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ✅ 外部連携（今後の拡張用）
class WordPressSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    site_url = db.Column(db.String(255), nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
