'''
Migration Test
'''
import pytest
from app import db


class TestUsersMigration:
    '''usersテーブルのマイグレーションテスト'''

    def test_database_tables_exist(self, app):
        '''テーブルが存在することを確認: db.create_all() で全テーブルが作成されているか'''
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        # 必須テーブルの存在確認
        assert 'users' in tables

    def test_users_table_columns(self, app):
        '''usersテーブルのカラムを確認'''
        inspector = db.inspect(db.engine)
        columns = {col['name']: col for col in inspector.get_columns('users')}

        # 必須カラムの存在確認
        assert 'id' in columns
        assert 'username' in columns
        assert 'email' in columns
        assert 'password_hash' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns

    def test_users_table_indexes(self, app):
        '''usersテーブルのインデックスを確認'''
        inspector = db.inspect(db.engine)
        indexes = {idx['name']: idx for idx in inspector.get_indexes('users')}

        # ユニークインデックスの存在確認
        assert 'ix_users_username' in indexes
        assert indexes['ix_users_username']['unique']

        assert 'ix_users_email' in indexes
        assert indexes['ix_users_email']['unique']


class TestTodosMigration:
    '''todosテーブルのマイグレーションテスト'''

    def test_todos_table_exists(self, app):
        '''todosテーブルが存在することを確認'''
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        assert 'todos' in tables

    def test_todos_table_columns(self, app):
        '''todosテーブルのカラムを確認'''
        inspector = db.inspect(db.engine)
        columns = {col['name']: col for col in inspector.get_columns('todos')}

        # 必須カラムの存在確認
        assert 'id' in columns
        assert 'title' in columns
        assert 'description' in columns
        assert 'completed' in columns
        assert 'user_id' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns

    def test_todos_table_foreign_keys(self, app):
        '''todosテーブルの外部キー制約を確認'''
        inspector = db.inspect(db.engine)
        foreign_keys = inspector.get_foreign_keys('todos')

        # 外部キーの存在確認
        assert len(foreign_keys) > 0

        # user_id の外部キー確認
        user_fk = next(
            (fk for fk in foreign_keys if 'user_id' in fk['constrained_columns']),
            None
        )
        assert user_fk is not None
        assert user_fk['referred_table'] == 'users'
        assert 'id' in user_fk['referred_columns']

        # カスケード削除確認（DB レベル）
        # ※ models/todo.py の ForeignKey に ondelete='CASCADE' が設定されている必要がある
        assert user_fk['options'].get('ondelete') == 'CASCADE'

    def test_todos_table_indexes(self, app):
        '''todosテーブルのインデックスを確認'''
        inspector = db.inspect(db.engine)
        indexes = {idx['name']: idx for idx in inspector.get_indexes('todos')}

        # 複合インデックスの存在確認（user_id + completed）
        # このインデックスは user_id 単体のクエリにも使われる（左端プレフィックスルール）
        assert 'ix_todos_user_id_completed' in indexes
        assert indexes['ix_todos_user_id_completed']['column_names'] == ['user_id', 'completed']