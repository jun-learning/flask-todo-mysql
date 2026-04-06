'''
認証フォーム
'''
from flask_wtf import FlaskForm  # CSRF 保護付きフォームの基底クラス
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,    # 入力必須チェック
    Email,           # メールアドレス形式チェック
    Length,          # 文字数チェック
    EqualTo,         # 別フィールドとの一致チェック（パスワード確認用）
    ValidationError, # カスタムバリデーションエラー
    Regexp           # 正規表現チェック
)
from app.models.user import User


class SignupForm(FlaskForm):
    '''ユーザー登録フォーム'''

    username = StringField(
        'ユーザー名',
        validators=[
            DataRequired(message='ユーザー名は必須です'),
            Length(min=3, max=20, message='ユーザー名は3〜20文字で入力してください'),
            Regexp(
                r'^[a-zA-Z0-9_]+$',  # 英数字とアンダースコアのみ許可
                message='ユーザー名は英数字とアンダースコアのみ使用できます'
            )
        ]
    )

    email = StringField(
        'メールアドレス',
        validators=[
            DataRequired(message='メールアドレスは必須です'),
            Email(message='有効なメールアドレスを入力してください'),
            Length(max=120, message='メールアドレスは120文字以内で入力してください')
        ]
    )

    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(message='パスワードは必須です'),
            Length(min=8, message='パスワードは8文字以上で入力してください')
        ]
    )

    password_confirm = PasswordField(
        'パスワード（確認）',
        validators=[
            DataRequired(message='パスワード（確認）は必須です'),
            EqualTo('password', message='パスワードが一致しません')  # 'password' フィールドと同じ値か確認
        ]
    )

    submit = SubmitField('登録')

    def validate_username(self, username):
        '''
        ユーザー名の重複チェック

        Flask-WTF は validate_フィールド名 というメソッドを自動で呼び出す。
        DB に既存ユーザーがいれば ValidationError を raise する。

        Raises:
            ValidationError: ユーザー名が既に使用されている場合
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('このユーザー名は既に使用されています')

    def validate_email(self, email):
        '''
        メールアドレスの重複チェック

        Raises:
            ValidationError: メールアドレスが既に使用されている場合
        '''
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('このメールアドレスは既に登録されています')


class LoginForm(FlaskForm):
    '''ログインフォーム'''

    identifier = StringField(
        'ユーザー名またはメールアドレス',
        validators=[
            DataRequired(message='ユーザー名またはメールアドレスは必須です')
        ]
    )

    password = PasswordField(
        'パスワード',
        validators=[
            DataRequired(message='パスワードは必須です')
        ]
    )

    remember_me = BooleanField('ログイン状態を保持')  # チェックボックス（True/False）

    submit = SubmitField('ログイン')