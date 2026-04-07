'''
CSRF Protection Test
'''
import pytest


class TestCSRFProtection:
    '''CSRF保護のテスト'''

    def test_csrf_token_in_signup_form(self, csrf_client):
        '''ユーザー登録フォームにCSRFトークンが含まれているか'''
        response = csrf_client.get('/auth/signup')
        assert b'csrf_token' in response.data

    def test_csrf_token_in_login_form(self, csrf_client):
        '''ログインフォームにCSRFトークンが含まれているか'''
        response = csrf_client.get('/auth/login')
        assert b'csrf_token' in response.data

    def test_signup_without_csrf_token_fails(self, csrf_client):
        '''CSRFトークンなしでユーザー登録すると失敗'''
        response = csrf_client.post(
            '/auth/signup',
            data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'password_confirm': 'password123'
            },
            follow_redirects=False
        )
        assert response.status_code == 400

    def test_login_without_csrf_token_fails(self, csrf_client):
        '''CSRFトークンなしでログインすると失敗'''
        response = csrf_client.post(
            '/auth/login',
            data={
                'identifier': 'testuser',
                'password': 'password123'
            },
            follow_redirects=False
        )
        assert response.status_code == 400