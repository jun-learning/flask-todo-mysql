'''
Migration Test
'''
import pytest
from flask import Flask
from app import db, create_app
from app.models.user import User


class TestMigrations:
    '''マイグレーションのテスト'''

    def test_database_tables_exist(self, app):
        '''テーブルが存在することを確認: db.create_all() で全テーブルが作成されているか'''
        # テーブル名取得（inspect は DB のメタ情報を調べるためのツール）
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()

        # 必須テーブルの存在確認
        assert 'users' in tables
        # assert 'alembic_version' in tables

    def test_users_table_columns(self, app):
        '''usersテーブルのカラムを確認: モデル定義通りのカラムが存在するか'''
        inspector = db.inspect(db.engine)
        columns = {col['name']: col for col in inspector.get_columns('users')}

        # 必須カラムの存在確認
        assert 'id' in columns
        assert 'username' in columns
        assert 'email' in columns
        assert 'password_hash' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns

        # 型確認
        assert columns['id']['type'].__class__.__name__ == 'INTEGER'
        assert 'VARCHAR' in str(columns['username']['type'])
        assert 'VARCHAR' in str(columns['email']['type'])

    def test_users_table_indexes(self, app):
        '''usersテーブルのインデックスを確認: unique=True のインデックスが作成されているか'''
        inspector = db.inspect(db.engine)
        indexes = {idx['name']: idx for idx in inspector.get_indexes('users')}

        # ユニークインデックスの存在確認
        assert 'ix_users_username' in indexes
        assert 'ix_users_email' in indexes

        # ユニーク制約確認（unique=True で登録時の重複チェックが有効になる）
        assert indexes['ix_users_username']['unique']
        assert indexes['ix_users_email']['unique']