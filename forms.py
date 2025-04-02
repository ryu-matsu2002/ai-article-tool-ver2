# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, URL
from wtforms import EmailField, PasswordField
from wtforms.validators import Email, Length, EqualTo

class RegisterForm(FlaskForm):
    email = EmailField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('パスワード確認', validators=[EqualTo('password')])
    submit = SubmitField('登録')

class LoginForm(FlaskForm):
    email = EmailField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')


# ✅ 記事ジャンル入力用フォーム（初期のもの）
class GenreForm(FlaskForm):
    genre = StringField('記事ジャンル', validators=[DataRequired()])
    submit = SubmitField('生成開始')

# ✅ WordPressサイト登録用フォーム（個別使用時）
class SiteRegisterForm(FlaskForm):
    site_name = StringField('サイト名', validators=[DataRequired()])
    wp_url = StringField('WordPressサイトURL', validators=[DataRequired(), URL()])
    wp_username = StringField('WordPressユーザー名', validators=[DataRequired()])
    wp_app_password = PasswordField('アプリケーションパスワード', validators=[DataRequired()])
    submit = SubmitField('サイトを登録する')

# ✅ 記事編集フォーム
class ArticleEditForm(FlaskForm):
    title = StringField('記事タイトル', validators=[DataRequired()])
    content = TextAreaField('記事本文', validators=[DataRequired()])
    submit = SubmitField('更新する')

# ✅ ジャンル＋サイト情報 一括入力フォーム（CombinedForm）
class CombinedForm(FlaskForm):
    genre = StringField('記事ジャンル', validators=[DataRequired()])
    site_name = StringField('サイト名', validators=[DataRequired()])
    wp_url = StringField('WordPress URL', validators=[DataRequired(), URL()])
    wp_username = StringField('ユーザー名', validators=[DataRequired()])
    wp_app_password = PasswordField('アプリケーションパスワード', validators=[DataRequired()])
    submit = SubmitField('記事を自動生成＆投稿開始')
