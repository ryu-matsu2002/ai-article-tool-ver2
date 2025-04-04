from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.security import check_password_hash

from extensions import db
from models import Site, Article, PostLog, User
from article_generator import generate_article
from utils.logger import log_article_progress
from forms import LoginForm

main = Blueprint('main', __name__)

# 🔐 ログインページ（login_manager.login_view 用）
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('❌ メールアドレスまたはパスワードが正しくありません。')
    return render_template('login.html', form=form)

# 🚪 ログアウト機能（←追加）
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("👋 ログアウトしました。")
    return redirect(url_for('main.login'))

# ✅ ダッシュボード
@main.route('/')
@login_required
def index():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', sites=sites)

# ✅ 投稿ログ
@main.route('/post_log')
@login_required
def post_log():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('post_log.html', sites=sites)

# ✅ サイト一括削除
@main.route('/delete_sites', methods=['POST'])
@login_required
def delete_sites():
    selected_ids = request.form.getlist('site_ids')
    for site_id in selected_ids:
        site = Site.query.get(site_id)
        if site and site.user_id == current_user.id:
            Article.query.filter_by(site_id=site.id).delete()
            PostLog.query.filter_by(site_id=site.id).delete()
            db.session.delete(site)
    db.session.commit()
    flash('🗑️ 選択したサイト情報を削除しました。')
    return redirect(url_for('main.index'))

# ✅ 記事の再投稿
@main.route('/retry_post/<int:article_id>')
@login_required
def retry_post(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('⚠️ 不正な操作です。')
        return redirect(url_for('main.post_log'))

    article.status = 'pending'
    db.session.commit()
    flash("🔄 記事を再投稿対象に戻しました。")
    return redirect(url_for('main.post_log'))

# ✅ 記事の削除
@main.route('/delete_article/<int:article_id>')
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('⚠️ 不正な操作です。')
        return redirect(url_for('main.post_log'))

    db.session.delete(article)
    db.session.commit()
    flash("🗑️ 記事を削除しました。")
    return redirect(url_for('main.post_log'))
