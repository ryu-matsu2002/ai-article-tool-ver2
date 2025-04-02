# routes.py
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import (
    CombinedForm, SiteRegisterForm, ArticleEditForm,
    RegisterForm, LoginForm
)
from models import db, Article, Site, User
from bulk_article_generator import generate_bulk_articles
from flask import flash, redirect, url_for
from models import WordPressSite
from flask_login import current_user, login_required
from app import app

main = Blueprint('main', __name__)


# 🔐 ユーザー登録
@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(email=form.email.data, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('✅ 登録完了しました。ログインしてください。')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)


# 🔐 ログイン
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('✅ ログイン成功！')
            return redirect(url_for('main.index'))
        else:
            flash('❌ メールアドレスまたはパスワードが違います。')
    return render_template('login.html', form=form)


# 🔐 ログアウト
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('👋 ログアウトしました')
    return redirect(url_for('main.login'))


# ✅ トップ（ジャンル＋サイト入力 → 自動投稿開始）
@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CombinedForm()
    if form.validate_on_submit():
        genre = form.genre.data

        # サイト重複チェック（同URLなら再利用）
        wp_url = form.wp_url.data.rstrip('/')
        site = Site.query.filter_by(wp_url=wp_url, user_id=current_user.id).first()
        if not site:
            site = Site(
                user_id=current_user.id,
                site_name=form.site_name.data,
                wp_url=wp_url,
                wp_username=form.wp_username.data,
                wp_app_password=form.wp_app_password.data
            )
            db.session.add(site)
            db.session.commit()

        generate_bulk_articles(genre, site.id, current_user.id)

        flash('✅ サイト情報を登録し、10記事を自動生成しました。自動投稿が開始されます。')
        return redirect(url_for('main.post_log'))

    return render_template('index.html', form=form)


# ✅ 投稿ログ画面
@main.route('/post-log')
@login_required
def post_log():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    articles = Article.query.filter_by(user_id=current_user.id).order_by(Article.created_at.desc()).all()

    # 投稿済み10件でジャンル入力を促す
    posted_count = sum(1 for a in articles if a.status == 'posted')
    if posted_count > 0 and posted_count % 10 == 0:
        flash("🎉 10記事の投稿が完了しました！次のジャンルを入力して続きを自動投稿しましょう。")
        return redirect(url_for('main.index'))

    return render_template("post_log.html", articles=articles)


# ✅ サイト登録（個別用）
@main.route('/register-site', methods=['GET', 'POST'])
@login_required
def register_site():
    form = SiteRegisterForm()
    if form.validate_on_submit():
        new_site = Site(
            user_id=current_user.id,
            site_name=form.site_name.data,
            wp_url=form.wp_url.data.rstrip("/"),
            wp_username=form.wp_username.data,
            wp_app_password=form.wp_app_password.data
        )
        db.session.add(new_site)
        db.session.commit()
        flash('✅ サイトが登録されました')
        return redirect(url_for('main.index'))
    return render_template('register_site.html', form=form)


# 🔍 記事プレビュー
@main.route('/article/<int:article_id>')
@login_required
def article_detail(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash("⚠️ 記事の閲覧権限がありません。")
        return redirect(url_for('main.post_log'))
    return render_template('article_detail.html', article=article)


# ✏️ 記事編集
@main.route('/edit-article/<int:article_id>', methods=["GET", "POST"])
@login_required
def edit_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash("⚠️ 編集権限がありません。")
        return redirect(url_for('main.post_log'))

    form = ArticleEditForm(obj=article)
    if form.validate_on_submit():
        article.title = form.title.data
        article.content = form.content.data
        db.session.commit()
        flash("✅ 記事を更新しました！")
        return redirect(url_for('main.post_log'))
    return render_template('edit_article.html', form=form, article=article)


# 🔄 再投稿処理
@main.route('/retry-post/<int:article_id>', methods=["POST"])
@login_required
def retry_post(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash("⚠️ 操作権限がありません。")
        return redirect(url_for('main.post_log'))

    if article.status == "failed":
        article.status = "pending"
        db.session.commit()
        flash("🔄 記事を再投稿対象に戻しました。")
    return redirect(url_for('main.post_log'))

@app.route('/delete_sites', methods=['POST'])
@login_required
def delete_sites():
    WordPressSite.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('登録サイト情報をすべて削除しました。')
    return redirect(url_for('dashboard'))  # 適切な遷移先に変更