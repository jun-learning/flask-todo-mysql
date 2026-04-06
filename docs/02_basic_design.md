# 基本設計書

## システム構成図

### 全体構成

    ブラウザ
      ↓ HTTP
    Flask アプリケーション（Docker コンテナ）
      ↓ SQL
    MySQL 8.0（Docker コンテナ）

### レイヤー構成

    プレゼンテーション層: テンプレート（Jinja2）+ 静的ファイル（CSS/JS）
      ↓
    アプリケーション層: Blueprint（auth / todos / main）
      ↓
    ビジネスロジック層: モデル（User / Todo）+ フォーム（WTForms）
      ↓
    データアクセス層: SQLAlchemy ORM
      ↓
    データベース層: MySQL 8.0

---

## ディレクトリ構造

    flask-todo-mysql/
    ├── app/
    │   ├── __init__.py              # Application Factory
    │   ├── config.py                # 設定ファイル
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── user.py              # Userモデル
    │   │   └── todo.py              # Todoモデル
    │   ├── blueprints/
    │   │   ├── __init__.py
    │   │   ├── auth.py              # 認証（登録、ログイン、ログアウト）
    │   │   ├── todos.py             # ToDo CRUD
    │   │   └── main.py              # トップページ、ヘルスチェック
    │   ├── forms/
    │   │   ├── __init__.py
    │   │   ├── auth_forms.py        # 認証フォーム
    │   │   └── todo_forms.py        # ToDoフォーム
    │   ├── templates/
    │   │   ├── base.html            # ベーステンプレート
    │   │   ├── index.html           # トップページ
    │   │   ├── auth/
    │   │   │   ├── signup.html      # ユーザー登録
    │   │   │   └── login.html       # ログイン
    │   │   ├── todos/
    │   │   │   ├── list.html        # ToDo一覧
    │   │   │   ├── detail.html      # ToDo詳細
    │   │   │   ├── new.html         # ToDo作成
    │   │   │   └── edit.html        # ToDo編集
    │   │   └── errors/
    │   │       ├── 404.html         # 404エラー
    │   │       ├── 403.html         # 403エラー
    │   │       └── 500.html         # 500エラー
    │   └── static/
    │       ├── css/
    │       │   └── style.css        # カスタムCSS
    │       └── js/
    │           └── main.js          # カスタムJS
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py              # pytest設定
    │   ├── test_models.py           # モデルテスト
    │   ├── test_auth.py             # 認証テスト
    │   ├── test_todos.py            # ToDoテスト
    │   ├── test_security.py         # セキュリティテスト
    │   └── test_migrations.py       # マイグレーションテスト
    ├── migrations/                  # DBマイグレーション
    │   ├── versions/
    │   └── ...
    ├── docs/                        # ドキュメント
    │   ├── 01_requirements.md
    │   ├── 02_basic_design.md
    │   └── ...
    ├── scripts/                     # 補助スクリプト
    │   ├── init.sql
    │   └── reset_db.sh
    ├── docker-compose.yml           # 開発環境
    ├── docker-compose.gunicorn.yml  # Gunicorn環境
    ├── docker-compose.uwsgi.yml     # uWSGI環境
    ├── Dockerfile
    ├── Dockerfile.gunicorn
    ├── Dockerfile.uwsgi
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── Makefile
    └── run.py                       # アプリケーション起動

---

## ER図（Entity-Relationship Diagram）

### テーブル関係図

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


### テーブル詳細定義

#### users テーブル

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|-----|------|------------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | ユーザーID |
| username | VARCHAR(80) | NOT NULL, UNIQUE | - | ユーザー名（3〜20文字、英数字とアンダースコア） |
| email | VARCHAR(120) | NOT NULL, UNIQUE | - | メールアドレス（有効な形式） |
| password_hash | VARCHAR(255) | NOT NULL | - | bcryptでハッシュ化されたパスワード |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

**インデックス:**
- PRIMARY KEY: `id`
- UNIQUE INDEX: `ix_users_username` on `username`
- UNIQUE INDEX: `ix_users_email` on `email`

#### todos テーブル

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|----------|-----|------|------------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | - | ToDo ID |
| title | VARCHAR(100) | NOT NULL | - | タイトル（1〜100文字） |
| description | TEXT | NULL | - | 説明（500文字以内） |
| completed | BOOLEAN | NOT NULL | FALSE | 完了フラグ |
| user_id | INT | NOT NULL, FOREIGN KEY | - | ユーザーID（外部キー） |
| created_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP | 作成日時 |
| updated_at | DATETIME | NOT NULL | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新日時 |

**インデックス:**
- PRIMARY KEY: `id`
- INDEX: `ix_todos_user_id` on `user_id`
- INDEX: `ix_todos_user_id_completed` on `(user_id, completed)` ← フィルター機能の高速化

**外部キー制約:**
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

### リレーションシップ詳細

**User - Todo (1:N)**
- **種類**: 1対多（One to Many）
- **関係**: 1人のユーザーは複数のToDoを持つ
- **実装**: SQLAlchemy relationship
- **外部キー**: `todos.user_id` → `users.id`
- **カスケード削除**: ユーザー削除時、関連するToDoも自動削除

---

## 画面遷移図

    [トップページ /]
      ├─ 未ログイン → [ユーザー登録 /signup] → 登録成功 → [ログイン /login]
      │                                                         ↓ 認証成功
      └─ ログイン済み ──────────────────────────────→ [ToDoリスト /todos]
                                                            ├─ [ToDo作成 /todos/new] → 保存 → [ToDoリスト]
                                                            ├─ [ToDo詳細 /todos/<id>]
                                                            │     ├─ [ToDo編集 /todos/<id>/edit] → 更新 → [ToDo詳細]
                                                            │     └─ 削除 → [ToDoリスト]
                                                            └─ ログアウト → [トップページ]

---

## ルーティング設計

### 認証関連（auth Blueprint）

**URLプレフィックス:** `/auth`

| メソッド | パス | 関数 | 説明 | 認証 | リダイレクト先 |
|---------|------|------|------|------|--------------|
| GET | `/signup` | signup() | ユーザー登録フォーム表示 | 不要 | - |
| POST | `/signup` | signup() | ユーザー登録処理 | 不要 | `/login` (成功時) |
| GET | `/login` | login() | ログインフォーム表示 | 不要 | - |
| POST | `/login` | login() | ログイン処理 | 不要 | `/todos` (成功時) |
| GET | `/logout` | logout() | ログアウト処理 | 必要 | `/` |

### ToDo関連（todos Blueprint）

**URLプレフィックス:** `/todos`

| メソッド | パス | 関数 | 説明 | 認証 | リダイレクト先 |
|---------|------|------|------|------|--------------|
| GET | `/` | index() | ToDoリスト表示 | 必要 | - |
| GET | `/new` | new() | ToDo作成フォーム表示 | 必要 | - |
| POST | `/new` | new() | ToDo作成処理 | 必要 | `/todos` (成功時) |
| GET | `/<int:id>` | show(id) | ToDo詳細表示 | 必要 | - |
| GET | `/<int:id>/edit` | edit(id) | ToDo編集フォーム表示 | 必要 | - |
| POST | `/<int:id>/edit` | edit(id) | ToDo更新処理 | 必要 | `/todos/<id>` (成功時) |
| POST | `/<int:id>/delete` | delete(id) | ToDo削除処理 | 必要 | `/todos` |
| POST | `/<int:id>/toggle` | toggle(id) | 完了/未完了切り替え | 必要 | `/todos` |

### メイン（main Blueprint）

**URLプレフィックス:** なし

| メソッド | パス | 関数 | 説明 | 認証 | リダイレクト先 |
|---------|------|------|------|------|--------------|
| GET | `/` | index() | トップページ | 不要 | - |
| GET | `/health` | health() | ヘルスチェック | 不要 | - |

---

## 画面設計（ワイヤーフレーム）

### 1. トップページ (`/`)

    +----------------------------------+
    |  [Logo] ToDo App    [ログイン][登録] |
    +----------------------------------+
    |                                  |
    |        ToDo App へようこそ          |
    |                                  |
    |   シンプルで使いやすいToDo管理      |
    |                                  |
    |    [ユーザー登録]  [ログイン]       |
    |                                  |
    +----------------------------------+
    |        © 2024 ToDo App           |
    +----------------------------------+

### 2. ユーザー登録ページ (`/signup`)

    +----------------------------------+
    |  [Logo] ToDo App         [戻る]   |
    +----------------------------------+
    |                                  |
    |       ユーザー登録                 |
    |                                  |
    |  ユーザー名 [____________]         |
    |  メール    [____________]         |
    |  パスワード [____________]         |
    |  確認      [____________]         |
    |                                  |
    |         [登録する]                |
    |                                  |
    |  既にアカウントをお持ちですか？      |
    |  [ログイン]                       |
    |                                  |
    +----------------------------------+

### 3. ログインページ (`/login`)

    +----------------------------------+
    |  [Logo] ToDo App         [戻る]   |
    +----------------------------------+
    |                                  |
    |          ログイン                  |
    |                                  |
    |  ユーザー名/メール [____________]   |
    |  パスワード       [____________]   |
    |                                  |
    |  [ ] ログイン状態を保持            |
    |                                  |
    |         [ログイン]                |
    |                                  |
    |  アカウントをお持ちでないですか？    |
    |  [ユーザー登録]                   |
    |                                  |
    +----------------------------------+

### 4. ToDoリストページ (`/todos`)

    +----------------------------------+
    |  ToDo App  [username] [ログアウト]  |
    +----------------------------------+
    |  ToDoリスト          [+ 新規作成]   |
    |                                  |
    |  [全て] [未完了] [完了]            |
    |                                  |
    | +------------------------------+ |
    | | [✓] タスク1                    | |
    | |     説明文...                  | |
    | |     [編集] [削除]              | |
    | +------------------------------+ |
    | | [ ] タスク2                    | |
    | |     説明文...                  | |
    | |     [編集] [削除]              | |
    | +------------------------------+ |
    |                                  |
    +----------------------------------+

### 5. ToDo詳細ページ (`/todos/<id>`)

    +----------------------------------+
    |  ToDo App            [一覧に戻る]  |
    +----------------------------------+
    |                                  |
    |  [完了] バッジ                     |
    |                                  |
    |  タスクのタイトル                  |
    |                                  |
    |  【説明】                         |
    |  詳細な説明がここに表示されます      |
    |                                  |
    |  【詳細情報】                     |
    |  作成日時: 2024-01-26 10:00      |
    |  更新日時: 2024-01-26 15:30      |
    |  ステータス: 完了                  |
    |                                  |
    |  [編集] [削除]                    |
    |                                  |
    +----------------------------------+

---


## セキュリティ設計

### 1. 認証・認可

#### セッション管理

**セッション設定:**
- HttpOnly: JavaScriptからアクセス不可
- SameSite: Lax（CSRF対策）
- Secure: HTTPS環境でのみ送信（本番環境）
- 有効期限: 24時間

#### パスワード管理

    # パスワードハッシュ化
    bcrypt.generate_password_hash(password).decode('utf-8')

    # パスワード検証
    bcrypt.check_password_hash(password_hash, password)

**パスワード要件:**
- 最小8文字
- 英字と数字を含む（将来実装）

#### アクセス制御

    # ログイン必須
    @login_required
    def protected_route():
        pass

    # 所有者チェック
    if todo.user_id != current_user.id:
        abort(403)

### 2. CSRF対策

**実装:**
- Flask-WTFのCSRF保護を使用
- 全てのPOST/PUT/DELETEリクエストで検証
- トークンは隠しフィールドに自動挿入

### 3. XSS対策

**Jinja2自動エスケープ:**

    <!-- 安全: 自動的にエスケープされる -->
    <p>{{ user_input }}</p>

    <!-- 危険: 使用禁止 -->
    <p>{{ user_input|safe }}</p>

**エスケープ例:**

    入力: <script>alert('XSS')</script>
    出力: &lt;script&gt;alert('XSS')&lt;/script&gt;

### 4. SQLインジェクション対策

**SQLAlchemy ORM使用:**

    # 安全: パラメータは自動的にエスケープ
    user = User.query.filter_by(username=username).first()

    # 安全: パラメータバインディング
    user = User.query.filter(User.username == username).first()

    # 危険: 使用禁止
    query = f'SELECT * FROM users WHERE username = "{username}"'

### 5. セキュリティヘッダー

    @app.after_request
    def set_security_headers(response):
        # MIMEスニッフィング防止
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # クリックジャッキング防止
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # XSSフィルター有効化
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # HTTPS強制（本番環境のみ）
        if app.config.get('ENV') == 'production':
            response.headers['Strict-Transport-Security'] = \\
                'max-age=31536000; includeSubDomains'

        return response

---

## エラーハンドリング

### HTTPエラー

| ステータスコード | 説明 | 表示内容 |
|----------------|------|---------|
| 400 | Bad Request | 不正なリクエストです（CSRFエラー等） |
| 401 | Unauthorized | ログインが必要です |
| 403 | Forbidden | アクセス権限がありません |
| 404 | Not Found | ページが見つかりません |
| 500 | Internal Server Error | サーバーエラーが発生しました |

### バリデーションエラー
- フォーム送信時にバリデーションエラーがある場合
- エラーメッセージをフォームの各フィールドに表示
- 入力値は保持される（再入力不要）

### データベースエラー
- コネクションエラー: リトライ（最大3回）
- デッドロック: 自動リトライ
- その他: ログに記録し、500エラーを返す

---

## パフォーマンス設計

### データベースクエリ最適化

**インデックス設計:**

    -- users
    CREATE UNIQUE INDEX ix_users_username ON users(username);
    CREATE UNIQUE INDEX ix_users_email ON users(email);

    -- todos
    CREATE INDEX ix_todos_user_id ON todos(user_id);
    CREATE INDEX ix_todos_user_id_completed ON todos(user_id, completed);

**N+1問題の回避:**

    # 悪い例: N+1問題が発生
    users = User.query.all()
    for user in users:
        print(user.todos.count())  # 各ユーザーごとにクエリ実行

    # 良い例: JOINで一度に取得
    users = User.query.options(joinedload(User.todos)).all()
    for user in users:
        print(len(user.todos))  # 追加クエリなし

### キャッシュ戦略（Phase 2以降）
- セッションキャッシュ: Flask-Session
- クエリキャッシュ: Flask-Caching
- 静的ファイル: CDN

---

## デプロイ構成

### 開発環境

    Browser → Flask Development Server (port 5000)
                ↓
              MySQL (Docker)

### ステージング/本番環境（Gunicorn）

    Browser → Nginx (port 80/443)
                ↓
              Gunicorn (port 8000, 4 workers)
                ↓
              Flask Application
                ↓
              MySQL (Docker/RDS)

### ステージング/本番環境（uWSGI）

    Browser → Nginx (port 80/443)
                ↓
              uWSGI (UNIX socket, 4 processes × 2 threads)
                ↓
              Flask Application
                ↓
              MySQL (Docker/RDS)

---

## テスト戦略

### テストレベル

| テストレベル | 対象 | ツール | カバレッジ目標 |
|------------|------|--------|--------------|
| 単体テスト | Models, Forms | pytest | 90%以上 |
| 統合テスト | Blueprints, Routes | pytest | 85%以上 |
| E2Eテスト | 画面操作 | 手動 | 主要フロー |

### テストケース

**ユーザー登録:**
- 正常系: 有効な情報で登録成功
- 異常系: ユーザー名重複
- 異常系: メールアドレス重複
- 異常系: パスワード短すぎる

**ログイン:**
- 正常系: 正しい情報でログイン成功
- 異常系: 間違ったパスワード
- 異常系: 存在しないユーザー

**ToDo CRUD:**
- 作成: 正常系、バリデーションエラー
- 一覧: フィルター機能
- 詳細: 自分のToDo、他人のToDo
- 編集: 正常系、権限エラー
- 削除: 正常系、権限エラー

---

## モニタリング・ログ

### ログレベル

| レベル | 用途 | 例 |
|--------|------|-----|
| DEBUG | 開発時のデバッグ情報 | SQLクエリ、変数の値 |
| INFO | 通常の動作情報 | ユーザーログイン、ToDo作成 |
| WARNING | 警告（動作は継続） | バリデーションエラー |
| ERROR | エラー（処理失敗） | DB接続エラー |
| CRITICAL | 致命的エラー | アプリケーション起動失敗 |

### ログ出力例

    # ユーザー登録
    logger.info(f'New user registered: {username}')

    # ログイン
    logger.info(f'User logged in: {username}')

    # エラー
    logger.error(f'Database error: {str(e)}', exc_info=True)

---

## まとめ

この基本設計書では、以下を定義しました：

1. **システム構成**: Docker、Flask、MySQL
2. **ディレクトリ構造**: Application Factoryパターン
3. **データベース設計**: ER図、テーブル定義
4. **画面設計**: ワイヤーフレーム
5. **ルーティング**: RESTful設計
6. **セキュリティ**: 認証、CSRF、XSS、SQLインジェクション対策
7. **エラーハンドリング**: HTTPエラー、バリデーションエラー
8. **パフォーマンス**: インデックス、N+1問題対策
9. **デプロイ**: Gunicorn、uWSGI
10. **テスト**: 単体、統合、E2E

次のステップ: 詳細設計（Day 6-7で実装開始）