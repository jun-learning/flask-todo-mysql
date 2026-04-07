'''
Security Test
'''
import pytest


class TestSecurityHeaders:
    '''セキュリティヘッダーのテスト'''

    def test_x_content_type_options_header(self, client):
        '''X-Content-Type-Optionsヘッダーが設定されているか'''
        response = client.get('/')
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'

    def test_x_frame_options_header(self, client):
        '''X-Frame-Optionsヘッダーが設定されているか'''
        response = client.get('/')
        assert response.headers.get('X-Frame-Options') == 'SAMEORIGIN'

    def test_x_xss_protection_header(self, client):
        '''X-XSS-Protectionヘッダーが設定されているか'''
        response = client.get('/')
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'


class TestXSSProtection:
    '''XSS保護のテスト'''

    def test_jinja2_auto_escape(self, app):
        '''Jinja2の自動エスケープが有効か: render_template_string で直接確認'''
        from flask import render_template_string

        with app.app_context():
            # 悪意のあるスクリプトをテンプレートに渡す
            malicious_input = "<script>alert('XSS')</script>"
            result = render_template_string("{{ user_input }}", user_input=malicious_input)

            # <script> がそのまま出力されていないこと
            assert '<script>' not in result
            # エスケープされた形で出力されていること
            assert '&lt;script&gt;' in result


class TestSQLInjectionProtection:
    '''SQLインジェクション保護のテスト'''

    def test_sql_injection_in_login(self, client, user):
        '''ログイン時のSQLインジェクション対策'''
        response = client.post('/auth/login', data={
            'identifier': "admin' OR '1'='1",
            'password': 'anything'
        })

        # ログインは失敗するはず（ログインページにとどまる）
        assert response.status_code == 200
        # レスポンスをデコードして日本語も含めて検証
        response_text = response.data.decode('utf-8')
        assert 'incorrect' in response_text.lower() or \
               'invalid' in response_text.lower() or \
               '正しくありません' in response_text