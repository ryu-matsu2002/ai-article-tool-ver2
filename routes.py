from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from forms import (
    CombinedForm, SiteRegisterForm, ArticleEditForm,
    RegisterForm, LoginForm
)
from models import db, Article, Site, User, WordPressSite
from bulk_article_generator import generate_bulk_articles
from utils.async_article_generator import generate_articles_safely  # 追加
import threading  # 追加

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

# ✅ トップ（ジャンル＋サイト入力 → 投稿ログに進む）
@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = CombinedForm()
    if form.validate_on_submit():
        genre = form.genre.data
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

        flash('✅ サイト情報を登録しました。投稿ログページで進捗を確認できます。')
        return redirect(url_for('main.post_log'))

    return render_template('index.html', form=form)

# ✅ 記事生成処理（非同期スレッド）
@main.route('/start-generation', methods=['POST'])
@login_required
def start_generation():
    genre = request.form.get("genre")
    site_id = int(request.form.get("site_id"))

    thread = threading.Thread(
        target=generate_articles_safely,
        args=(genre, site_id, current_user.id)
    )
    thread.start()

    flash("✅ インターバル付きで10記事の生成を開始しました。投稿ログから確認できます。")
    return redirect(url_for("main.post_log"))

# ✅ 投稿ログ画面
@main.route('/post-log')
@login_required
def post_log():
    site_id = request.args.get("site_id", type=int)
    status = request.args.get("status")

    user_sites = Site.query.filter_by(user_id=current_user.id).all()
    query = Article.query.filter_by(user_id=current_user.id)
    if site_id:
        query = query.filter_by(site_id=site_id)
    if status:
        query = query.filter_by(status=status)

    articles = query.order_by(Article.created_at.desc()).all()

    posted_count = sum(1 for a in articles if a.status == 'posted')
    if posted_count > 0 and posted_count % 10 == 0:
        flash("🎉 10記事の投稿が完了しました！次のジャンルを入力して続きを自動投稿しましょう。")
        return redirect(url_for('main.index'))

    return render_template(
        "post_log.html",
        articles=articles,
        user_sites=user_sites,
        selected_site_id=site_id,
        selected_status=status
    )

# ✅ サイト登録（個別）
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

# 🔍 記事詳細表示
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

# 🔄 再投稿
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

# 🗑 サイト情報の一括削除
@main.route('/delete_sites', methods=['POST'])
@login_required
def delete_sites():
    WordPressSite.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('🗑 登録サイト情報をすべて削除しました。')
    return redirect(url_for('main.index'))
