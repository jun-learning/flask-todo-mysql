'''
pytest設定ファイル
'''
import pytest
from app import create_app, db    # Application Factory と DB インスタンス
from app.models.user import User


@pytest.fixture
def app():
    '''テスト用Flaskアプリケーション'''
    # 'testing' 設定でアプリを作成（テスト用 DB、CSRF 無効等の設定が適用される）
    app = create_app('testing')

    with app.app_context():
        # --- テスト前処理 ---
        db.create_all()   # テスト用 DB に全テーブルを作成
        yield app         # テスト関数に app を渡す（ここでテストが実行される）
        # --- テスト後処理 ---
        db.session.remove()  # DB セッションをクローズ
        db.drop_all()        # テスト用 DB の全テーブルを削除（テストを独立させる）


@pytest.fixture
def client(app):
    '''テストクライアント（HTTP リクエストをシミュレートする）'''
    return app.test_client()


@pytest.fixture
def runner(app):
    '''CLIランナー（flask コマンドをテストで実行するため）'''
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    '''テスト用ユーザー（テストで「既存ユーザー」が必要な場合に使う）'''
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')  # ハッシュ化してから DB に保存

    db.session.add(user)    # セッションに追加（この時点では DB に未反映）
    db.session.commit()     # DB にコミット（確定保存）

    return user  # テスト関数に User オブジェクトを渡す


@pytest.fixture
def csrf_app():
    '''CSRF保護が有効なテスト用アプリ（CSRFテスト専用）'''
    app = create_app('testing')
    # テスト設定で無効化されたCSRFを強制的に有効化
    app.config['WTF_CSRF_ENABLED'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def csrf_client(csrf_app):
    '''CSRF保護が有効なテストクライアント'''
    return csrf_app.test_client()