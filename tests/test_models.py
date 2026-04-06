'''
Models Test
'''
import pytest
from app.models.user import User
from app import db


class TestUserModel:
    '''Userモデルのテスト'''

    def test_create_user(self, app):
        '''ユーザー作成テスト: User オブジェクトが正しく DB に保存されるか確認'''
        user = User(
            username='newuser',
            email='newuser@example.com'
        )
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        # id は DB に保存後に自動採番される
        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.password_hash is not None
        assert user.password_hash != 'password123'  # 平文では保存されていないことを確認

    def test_password_hashing(self, app):
        '''パスワードハッシュ化テスト: 平文保存されず、照合は正しく動くか確認'''
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        assert user.password_hash != 'password123'          # ハッシュ化されている
        assert user.check_password('password123')           # 正しいパスワードは True
        assert not user.check_password('wrongpassword')     # 間違いは False

    def test_unique_username(self, app, user):
        '''ユーザー名の一意制約テスト: 同じユーザー名の二重登録が拒否されるか確認'''
        duplicate_user = User(
            username='testuser',  # 既存のユーザー名
            email='another@example.com'
        )
        duplicate_user.set_password('password123')

        db.session.add(duplicate_user)

        # unique=True 制約違反で例外が発生することを確認
        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()  # 失敗したトランザクションをロールバック

    def test_unique_email(self, app, user):
        '''メールアドレスの一意制約テスト: 同じメールアドレスの二重登録が拒否されるか確認'''
        duplicate_user = User(
            username='anotheruser',
            email='test@example.com'  # 既存のメールアドレス
        )
        duplicate_user.set_password('password123')

        db.session.add(duplicate_user)

        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()

    def test_find_by_username_or_email(self, app, user):
        '''ユーザー名・メールアドレス検索テスト: OR 検索が正しく動くか確認'''
        # ユーザー名で検索
        found_user = User.find_by_username_or_email('testuser')
        assert found_user is not None
        assert found_user.id == user.id

        # メールアドレスで検索
        found_user = User.find_by_username_or_email('test@example.com')
        assert found_user is not None
        assert found_user.id == user.id

        # 存在しないユーザーは None が返る
        found_user = User.find_by_username_or_email('nonexistent')
        assert found_user is None

    def test_to_dict(self, app, user):
        '''辞書変換テスト: to_dict() がパスワードハッシュを含まないか確認'''
        user_dict = user.to_dict()

        assert user_dict['id'] == user.id
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert 'password_hash' not in user_dict  # セキュリティ上、パスワードハッシュは除外
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict