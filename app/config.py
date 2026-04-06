'''
アプリケーション設定
環境変数から設定値を読み込み、本番/開発/テストで切り替える
'''
import os
from datetime import timedelta


class Config:
    '''基本設定（全環境共通）'''

    # Secret Key: セッションの暗号化に使用。推測困難なランダム文字列を設定すること
    # os.environ.get() で環境変数を読み込み、なければデフォルト値を使う
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database: SQLAlchemy が使うDB接続URL
    # mysql+pymysql://ユーザー名:パスワード@ホスト:ポート/DB名 という形式
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:rootpassword@db:3306/flask_todo'

    # SQLAlchemy がモデルの変更を追跡する機能（不要なのでFalseにしてメモリ節約）
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLAlchemy が実行するSQLをターミナルに出力するか（本番はFalse）
    SQLALCHEMY_ECHO = False

    # Session: セッション（ログイン状態）の有効期限
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    # HttpOnly: JavaScript からセッションCookieにアクセス不可にする（XSS対策）
    SESSION_COOKIE_HTTPONLY = True

    # SameSite: 他サイトからのリクエストにCookieを送らない（CSRF対策）
    SESSION_COOKIE_SAMESITE = 'Lax'

    # WTF Forms: CSRF保護を有効にする
    WTF_CSRF_ENABLED = True

    # CSRFトークンの有効期限（Noneはセッション期限に従う）
    WTF_CSRF_TIME_LIMIT = None

    # 1ページに表示するToDoの件数
    TODOS_PER_PAGE = 20


class DevelopmentConfig(Config):
    '''開発環境設定（Config を継承し、必要な項目だけ上書き）'''
    DEBUG = True       # デバッグモード: エラー詳細表示、コード変更時の自動再起動
    TESTING = False
    SQLALCHEMY_ECHO = True   # 開発時は実行SQLをターミナルに出力して確認できるようにする


class TestingConfig(Config):
    '''テスト環境設定'''
    TESTING = True
    DEBUG = True

    # テスト用に専用のDBを使う（本番/開発DBのデータを破壊しないため）
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:rootpassword@db:3306/flask_todo_test'

    # テスト時はCSRFを無効化（テストコードからフォームを送信しやすくするため）
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    '''本番環境設定'''
    DEBUG = False    # 本番ではデバッグモードをオフ（エラー詳細が外部に漏れるのを防ぐ）
    TESTING = False

    # 本番環境では必ず環境変数から取得（デフォルト値を使わないようにする）
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Secure: HTTPS環境でのみCookieを送信（本番はHTTPS必須）
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'  # 本番はより厳格な Strict に変更


# 設定名 → 設定クラスのマッピング（create_app() で使用）
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig   # 環境変数が未設定の場合は development を使う
}