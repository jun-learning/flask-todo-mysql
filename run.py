'''
アプリケーション起動ファイル
docker compose または flask run から実行される
'''
import os
from app import create_app, db

# 環境変数 FLASK_ENV から設定名を取得（未設定なら 'development'）
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    '''
    Flask Shell（flask shell コマンド）で使える変数を定義
    デバッグ時に対話的にDBを操作するときに便利
    '''
    from app.models.user import User
    from app.models.todo import Todo

    return {
        'db': db,
        'User': User,
        'Todo': Todo
    }


@app.cli.command()
def init_db():
    '''データベース初期化（flask init-db コマンドで実行）'''
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def test():
    '''テスト実行（flask test コマンドで実行）'''
    import pytest
    pytest.main(['-v', 'tests/'])


if __name__ == '__main__':
    # python run.py で直接実行した場合（docker compose ではなくローカル実行時）
    app.run(host='0.0.0.0', port=5000)  # 0.0.0.0 でコンテナ外からもアクセス可能にする