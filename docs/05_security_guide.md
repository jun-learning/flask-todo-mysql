### セキュリティガイド

#### CSRF（Cross-Site Request Forgery）対策

##### CSRFとは

CSRF（クロスサイトリクエストフォージェリ）は、ユーザーが意図しないリクエストを
攻撃者が強制的に実行させる攻撃です。

##### 攻撃シナリオ

1. ユーザーが銀行サイトにログイン（セッション確立）
2. ユーザーが攻撃者のサイトにアクセス
3. 攻撃者のサイトが隠しフォームで銀行サイトに送金リクエスト
4. ブラウザがCookieを自動送信 → 銀行サイトは正規リクエストと判断
5. ユーザーの意図しない送金が実行される


##### Flask-WTFによるCSRF対策

Flask-WTFは自動的にCSRF対策を提供します。

###### 仕組み

1. サーバーがランダムなトークンを生成しセッションに保存
2. フォームの隠しフィールドにトークンを埋め込む
3. フォーム送信時、トークンも一緒に送信される
4. サーバーがセッションのトークンと送信されたトークンを照合
5. 一致すれば正規リクエスト、不一致なら拒否（403エラー）


###### 実装確認

**設定（app/config.py）:**

    class Config:
        WTF_CSRF_ENABLED = True  # CSRF保護有効
        WTF_CSRF_TIME_LIMIT = None  # トークン有効期限（セッション期限）

**Application Factory（app/__init__.py）:**

    from flask_wtf.csrf import CSRFProtect

    csrf = CSRFProtect()

    def create_app(config_name='default'):
        app = Flask(__name__)
        # ...
        csrf.init_app(app)
        # ...

**フォーム（app/forms/auth_forms.py）:**

    from flask_wtf import FlaskForm

    class SignupForm(FlaskForm):
        # FlaskFormを継承すると自動的にCSRF保護が有効
        pass

**テンプレート（app/templates/auth/signup.html）:**

    <form method='POST'>
        {{ form.hidden_tag() }}  <!-- CSRFトークンを含む隠しフィールド -->
        <!-- ... -->
    </form>

##### CSRF対策のテスト

正しく保護されているか確認します。

###### テストケース


1.**正常系：CSRFトークンありでフォーム送信**
   → 成功するはず

2.**異常系：CSRFトークンなしでフォーム送信**
   → 400 Bad Requestになるはず

3.**異常系：無効なCSRFトークンでフォーム送信**
   → 400 Bad Requestになるはず

##### AJAXリクエストのCSRF対策

AJAXでPOST/PUT/DELETEする場合もCSRFトークンが必要です。

###### 方法1: メタタグから取得

**テンプレート:**

    <meta name='csrf-token' content='{{ csrf_token() }}'>

**JavaScript:**

    const token = document.querySelector("meta[name='csrf-token']").content;

    fetch('/api/todos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': token
        },
        body: JSON.stringify(data)
    });

###### 方法2: Flask-WTF設定

    # app/config.py
    class Config:
        WTF_CSRF_HEADERS = ['X-CSRFToken', 'X-CSRF-Token']

##### ベストプラクティス

1.**常にCSRF保護を有効化**
   -全てのPOST/PUT/DELETEリクエストで保護

2.**例外は慎重に**
   -APIエンドポイント等で無効化する場合は、他の認証方法を使用

       @csrf.exempt
       @api_bp.route('/endpoint', methods=['POST'])
       def api_endpoint():
           # JWT等の他の認証を使用
           pass

3.**SameSite Cookie属性**

       # app/config.py
       SESSION_COOKIE_SAMESITE = 'Lax'  # または 'Strict'

4.**HTTPSの使用**
   -本番環境では必ずHTTPSを使用

       # app/config.py
       class ProductionConfig(Config):
           SESSION_COOKIE_SECURE = True  # HTTPS必須