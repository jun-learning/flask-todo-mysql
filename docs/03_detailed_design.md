### 詳細設計書

#### モデル詳細設計

##### User モデル

###### 責務
-ユーザー情報の管理
-パスワードのハッシュ化・検証
-ユーザー認証の提供

###### クラス図


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


###### メソッド詳細

**set_password(password: str)**
-目的: パスワードをハッシュ化して設定
-入力: 平文パスワード
-処理: bcryptでハッシュ化
-出力: なし（password_hashに設定）

**check_password(password: str) -> bool**
-目的: パスワードを検証
-入力: 平文パスワード
-処理: bcryptで検証
-出力: 正しければTrue、間違っていればFalse

**to_dict() -> dict**
-目的: 辞書形式に変換（JSONシリアライズ用）
-入力: なし
-処理: パスワードハッシュを除外して辞書化
-出力: ユーザー情報の辞書

**find_by_username_or_email(identifier: str) -> User**
-目的: ユーザー名またはメールアドレスで検索
-入力: ユーザー名またはメールアドレス
-処理: ORクエリで検索
-出力: Userオブジェクト（存在しない場合はNone）

###### セキュリティ考慮事項

**パスワードハッシュ化:**
-アルゴリズム: bcrypt
-ソルト: 自動生成
-ラウンド数: デフォルト（12）
-平文パスワードは保存しない

**一意制約:**
-ユーザー名: UNIQUE制約
-メールアドレス: UNIQUE制約
-インデックス: 検索パフォーマンス向上

###### バリデーション

**username:**
-必須
-3〜20文字
-英数字とアンダースコアのみ

**email:**
-必須
-有効なメールアドレス形式
-最大120文字

**password:**
-必須
-最小8文字
-英字と数字を含む（将来実装）