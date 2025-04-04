from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Site, Article, PostLog
from article_generator import generate_article
from post_scheduler import schedule_post
from utils.logger import log_article_progress

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', sites=sites)

@main.route('/post_log')
@login_required
def post_log():
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('post_log.html', sites=sites)

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
    flash('選択したサイト情報を削除しました。')
    return redirect(url_for('main.index'))

@main.route('/retry_post/<int:article_id>')
@login_required
def retry_post(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('不正な操作です。')
        return redirect(url_for('main.post_log'))

    article.status = 'pending'
    db.session.commit()
    flash("✅ 記事を再投稿対象に戻しました。")
    return redirect(url_for('main.post_log'))

@main.route('/delete_article/<int:article_id>')
@login_required
def delete_article(article_id):
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        flash('不正な操作です。')
        return redirect(url_for('main.post_log'))

    db.session.delete(article)
    db.session.commit()
    flash("🗑️ 記事を削除しました。")
    return redirect(url_for('main.post_log'))
