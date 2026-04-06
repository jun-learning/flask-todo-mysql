### マイグレーションガイド

#### Flask-Migrateとは

Flask-MigrateはAlembicをFlaskで使いやすくしたツールです。
データベースのスキーマ変更を管理し、バージョン管理します。

#### 基本的な流れ


**ER図（データベース構造）:**

    users (ユーザー)
      ├─ id (主キー)
      ├─ username (ユーザー名, UNIQUE)
      ├─ email (メールアドレス, UNIQUE)
      ├─ password_hash (パスワードハッシュ)
      ├─ created_at (作成日時)
      └─ updated_at (更新日時)
      │
      │ 1対多の関係
      ↓
    todos (ToDo)
      ├─ id (主キー)
      ├─ title (タイトル)
      ├─ description (説明)
      ├─ completed (完了フラグ)
      ├─ user_id (外部キー → users.id)
      ├─ created_at (作成日時)
      └─ updated_at (更新日時)


#### コマンド一覧

##### 初期化

    # Flask-Migrate初期化（最初の1回のみ）
    flask db init

##### マイグレーション生成

    # 自動生成
    flask db migrate -m '説明文'

    # 例：
    flask db migrate -m 'Add todos table'
    flask db migrate -m 'Add completed column to todos'

##### マイグレーション実行

    # 最新版まで適用
    flask db upgrade

    # 1つ戻る
    flask db downgrade

    # 特定バージョンに移行
    flask db upgrade <revision>
    flask db downgrade <revision>

##### 情報確認

    # 現在のバージョン
    flask db current

    # マイグレーション履歴
    flask db history

    # 詳細履歴
    flask db history --verbose

    # 次に実行されるマイグレーション
    flask db show

##### その他

    # 空のマイグレーションファイル作成（手動で編集する場合）
    flask db revision -m '説明文'

    # マイグレーションファイルのマージ
    flask db merge <revision1> <revision2>

    # ヘルプ
    flask db --help

#### マイグレーションファイルの構造

    '''説明文

    Revision ID: xxx  # このマイグレーションのID
    Revises: yyy      # 前のマイグレーションのID
    Create Date: 2024-01-26

    '''
    from alembic import op
    import sqlalchemy as sa

    # revision identifiers
    revision = 'xxx'
    down_revision = 'yyy'
    branch_labels = None
    depends_on = None


    def upgrade():
        '''アップグレード処理（新しいスキーマへ）'''
        pass


    def downgrade():
        '''ダウングレード処理（古いスキーマへ戻す）'''
        pass

#### ベストプラクティス

##### 1. マイグレーションファイルは必ず確認

自動生成されたマイグレーションファイルは必ず内容を確認し、
必要に応じて修正します。

    # 生成後、ファイルを確認
    cat migrations/versions/xxx_*.py

    # 問題があれば削除して再生成
    rm migrations/versions/xxx_*.py
    flask db migrate -m '修正版'

##### 2. upgradeとdowngradeは対称に

    def upgrade():
        op.create_table('users', ...)

    def downgrade():
        op.drop_table('users')  # upgradeの逆操作

##### 3. データベースバックアップ

本番環境では必ずバックアップを取ってから実行：

    # MySQL バックアップ
    # 注意: パスワードをコマンドライン引数に直接指定するとプロセスリストから漏洩する可能性があります。
    # 本番環境では ~/.my.cnf に認証情報を設定するか、MYSQL_PWD 環境変数の使用を検討してください。
    mysqldump -u root -p flask_todo > backup_$(date +%Y%m%d).sql

    # マイグレーション実行
    flask db upgrade

    # 問題があればロールバック
    flask db downgrade

##### 4. テスト環境で動作確認

    # テスト環境でマイグレーション実行
    FLASK_DEBUG=1 flask db upgrade

    # テスト実行
    pytest

    # 問題なければ本番環境で実行

#### よくあるエラーと対処法

##### エラー1: 'Target database is not up to date'

    # 原因: データベースのバージョンとマイグレーションファイルが一致していない

    # 対処:
    flask db stamp head  # 現在のスキーマを最新版として記録

##### エラー2: 'Can't locate revision identified by'

    # 原因: マイグレーションファイルが削除または移動された

    # 対処:
    # 1. データベースをリセット
    flask db downgrade base
    flask db upgrade

    # 2. または、alembic_versionテーブルを手動修正

##### エラー3: 'Table already exists'

    # 原因: テーブルが既に存在している

    # 対処:
    # 1. 既存テーブルを削除
    DROP TABLE tablename;

    # 2. または、マイグレーションファイルを修正
    op.create_table('tablename', ..., if_not_exists=True)

#### 開発フロー例

##### 新しいカラム追加

    # 1. モデルを編集
    # app/models/user.py に is_active カラムを追加

    # 2. マイグレーション生成
    flask db migrate -m 'Add is_active column to users'

    # 3. マイグレーションファイル確認
    cat migrations/versions/xxx_add_is_active_column_to_users.py

    # 4. マイグレーション実行
    flask db upgrade

    # 5. 確認
    flask db current

##### テーブル追加

    # 1. モデル作成
    # app/models/todo.py を作成

    # 2. マイグレーション生成
    flask db migrate -m 'Add todos table'

    # 3. マイグレーション実行
    flask db upgrade

#### まとめ

-モデル変更 → `flask db migrate` → 確認 → `flask db upgrade`
-必ずテスト環境で動作確認
-本番環境ではバックアップ必須
-マイグレーションファイルはGit管理