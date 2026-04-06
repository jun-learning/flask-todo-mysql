'''
Application Factory
Flask アプリとすべての拡張機能をここで初期化する
'''
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy    # ORM（データベース操作）
from flask_migrate import Migrate          # DBマイグレーション管理
from flask_login import LoginManager       # ログイン状態（セッション）管理
from flask_bcrypt import Bcrypt            # パスワードハッシュ化
from flask_wtf.csrf import CSRFProtect     # CSRF攻撃対策

from app.config import config

# 拡張機能インスタンスをここで作成（アプリとはまだ紐付けない）
# init_app() パターン: インスタンスをモジュールレベルで作り、
# create_app() 内で app と紐付けることで循環インポートを防ぐ
db = SQLAlchemy()       # DBセッション管理。まだ接続しない
migrate = Migrate()     # flask db コマンドを提供
login_manager = LoginManager()  # @login_required デコレータを提供
bcrypt = Bcrypt()       # bcrypt.generate_password_hash() / check_password_hash() を提供
csrf = CSRFProtect()    # 全フォームへの自動CSRFトークン付与


def create_app(config_name='default'):
    '''
    Application Factory
    この関数を呼ぶたびに新しい Flask アプリインスタンスが作られる（テストで便利）

    Args:
        config_name (str): 設定名（development, testing, production）

    Returns:
        Flask: Flaskアプリケーションインスタンス
    '''
    # __name__ でこのファイルの場所を Flask に伝える（テンプレートや静的ファイルの場所解決に使用）
    app = Flask(__name__)

    # config マッピングから設定クラスを選び、アプリに適用
    app.config.from_object(config[config_name])

    # 各拡張機能にアプリを紐付ける（この時点でDBへの接続が確立される）
    db.init_app(app)
    migrate.init_app(app, db)   # migrate は db も引数に取る（モデル変更の検出に必要）
    bcrypt.init_app(app)
    csrf.init_app(app)

    # Flask-Login の設定
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'           # 未ログイン時のリダイレクト先（Blueprint名.関数名）
    login_manager.login_message = 'ログインが必要です。'  # リダイレクト時に表示するメッセージ

    # user_loader: Flask-Login がセッションからユーザーを復元するときに呼ばれる関数
    # セッションに保存されたユーザーIDからUserオブジェクトを返す
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User  # 循環インポート回避のため関数内でimport
        return User.query.get(int(user_id))

    # モデルを import して SQLAlchemy のメタデータに登録
    # （この import がないと flask db migrate でテーブルが検出されない）
    from app import models
    
    # Blueprint を登録（各 Blueprint のルートがアプリに追加される）
    from app.blueprints.main import main_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.todos import todos_bp

    app.register_blueprint(main_bp)                        # / や /health
    app.register_blueprint(auth_bp, url_prefix='/auth')    # /auth/login, /auth/signup 等
    app.register_blueprint(todos_bp, url_prefix='/todos')  # /todos/, /todos/new 等

    # セキュリティヘッダー: 全レスポンスに自動付与
    @app.after_request
    def set_security_headers(response):
        # MIMEスニッフィング防止: ブラウザがファイル種別を勝手に解釈しないようにする
        response.headers['X-Content-Type-Options'] = 'nosniff'
        # クリックジャッキング防止: iframe への埋め込みを制限
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        # XSSフィルター有効化（古いブラウザ向け）
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # エラーハンドラー: 対応するHTTPエラー発生時にカスタムページを返す
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()  # DBエラー時はトランザクションをロールバックしてセッションをクリア
        return render_template('errors/500.html'), 500

    return app