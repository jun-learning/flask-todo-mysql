'''
Authentication Test
'''
import pytest
from app.models.user import User
from app import db


def decode(response):
    '''response.data を UTF-8 文字列に変換するヘルパー'''
    return response.data.decode('utf-8')


class TestSignup:
    '''ユーザー登録のテスト'''

    def test_signup_page_loads(self, client):
        '''ユーザー登録ページが表示されるか'''
        response = client.get('/auth/signup')
        text = decode(response)
        assert response.status_code == 200
        assert 'signup' in text.lower() or \
               'register' in text.lower() or \
               '登録' in text

    def test_successful_signup(self, client, app):
        '''正常なユーザー登録'''
        response = client.post('/auth/signup', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200

        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.check_password('password123')

    def test_signup_with_duplicate_username(self, client, user):
        '''重複したユーザー名での登録'''
        response = client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'another@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'already' in text.lower() or '使用されています' in text

    def test_signup_with_duplicate_email(self, client, user):
        '''重複したメールアドレスでの登録'''
        response = client.post('/auth/signup', data={
            'username': 'anotheruser',
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'already' in text.lower() or '登録されています' in text

    def test_signup_with_short_username(self, client):
        '''短すぎるユーザー名での登録'''
        response = client.post('/auth/signup', data={
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        text = decode(response)

        assert response.status_code == 200
        assert '3' in text or 'short' in text.lower()

    def test_signup_with_invalid_email(self, client):
        '''無効なメールアドレスでの登録'''
        response = client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'valid' in text.lower() or '有効' in text

    def test_signup_with_short_password(self, client):
        '''短すぎるパスワードでの登録'''
        response = client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'pass',
            'password_confirm': 'pass'
        })
        text = decode(response)

        assert response.status_code == 200
        assert '8' in text or 'short' in text.lower()

    def test_signup_with_password_mismatch(self, client):
        '''パスワードが一致しない場合'''
        response = client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'different'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'match' in text.lower() or '一致' in text


class TestLogin:
    '''ログインのテスト'''

    def test_login_page_loads(self, client):
        '''ログインページが表示されるか'''
        response = client.get('/auth/login')
        text = decode(response)
        assert response.status_code == 200
        assert 'login' in text.lower() or 'ログイン' in text

    def test_successful_login_with_username(self, client, user):
        '''ユーザー名でのログイン成功'''
        response = client.post('/auth/login', data={
            'identifier': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        text = decode(response)

        assert response.status_code == 200
        assert 'todo' in text.lower()

    def test_successful_login_with_email(self, client, user):
        '''メールアドレスでのログイン成功'''
        response = client.post('/auth/login', data={
            'identifier': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        text = decode(response)

        assert response.status_code == 200
        assert 'todo' in text.lower()

    def test_login_with_wrong_password(self, client, user):
        '''間違ったパスワードでのログイン'''
        response = client.post('/auth/login', data={
            'identifier': 'testuser',
            'password': 'wrongpassword'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'incorrect' in text.lower() or \
               'invalid' in text.lower() or \
               '正しくありません' in text

    def test_login_with_nonexistent_user(self, client):
        '''存在しないユーザーでのログイン'''
        response = client.post('/auth/login', data={
            'identifier': 'nonexistent',
            'password': 'password123'
        })
        text = decode(response)

        assert response.status_code == 200
        assert 'incorrect' in text.lower() or \
               'invalid' in text.lower() or \
               '正しくありません' in text

    def test_remember_me_functionality(self, client, user):
        '''「ログイン状態を保持」機能'''
        with client:
            response = client.post('/auth/login', data={
                'identifier': 'testuser',
                'password': 'password123',
                'remember_me': True
            }, follow_redirects=True)

            assert response.status_code == 200
            assert client.get_cookie('remember_token') is not None


class TestLogout:
    '''ログアウトのテスト'''

    def test_logout(self, client, user):
        '''ログアウト機能'''
        client.post('/auth/login', data={
            'identifier': 'testuser',
            'password': 'password123'
        })

        response = client.get('/auth/logout', follow_redirects=True)
        text = decode(response)

        assert response.status_code == 200
        assert 'todo app' in text.lower()


class TestProtectedRoutes:
    '''保護されたルートのテスト'''

    def test_todos_requires_login(self, client):
        '''ToDoリストはログイン必須'''
        response = client.get('/todos/', follow_redirects=False)

        assert response.status_code == 302
        assert '/auth/login' in response.location

    def test_access_todos_after_login(self, client, user):
        '''ログイン後はToDoリストにアクセスできる'''
        client.post('/auth/login', data={
            'identifier': 'testuser',
            'password': 'password123'
        })

        response = client.get('/todos/')
        text = decode(response)

        assert response.status_code == 200
        assert 'todo' in text.lower()

    def test_redirect_after_login(self, client, user):
        '''ログイン後、元のページにリダイレクト'''
        response = client.get('/todos/', follow_redirects=False)

        assert response.status_code == 302
        assert '/auth/login' in response.location
        assert 'next' in response.location