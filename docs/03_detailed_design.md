### 詳細設計書

#### モデル詳細設計

##### User モデル

###### 責務
-ユーザー情報の管理
-パスワードのハッシュ化・検証
-ユーザー認証の提供

### Todo モデル

#### 責務
-ToDo情報の管理
-完了状態の切り替え
-ユーザーごとのToDo取得・カウント

#### クラス図

**ER図（データベース構造）:**

```
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
```

### メソッド詳細

**toggle_completed() -> bool**
- 目的: 完了状態を切り替え
- 入力: なし
- 処理: completedフィールドをトグル
- 出力: 新しい完了状態

**to_dict() -> dict**
- 目的: 辞書形式に変換
- 入力: なし
- 処理: ToDo情報を辞書化
- 出力: ToDo情報の辞書

**get_user_todos(user_id: int, filter_type: str) -> list**
- 目的: ユーザーのToDoリストを取得
- 入力: ユーザーID、フィルタータイプ
- 処理: user_idで絞り込み、filter_typeでさらに絞り込み
- 出力: ToDoリスト

**count_user_todos(user_id: int, filter_type: str) -> int**
- 目的: ユーザーのToDo数をカウント
- 入力: ユーザーID、フィルタータイプ
- 処理: user_idで絞り込み、filter_typeでさらに絞り込んでカウント
- 出力: ToDo数

### バリデーション

**title:**
- 必須
- 1〜100文字

**description:**
- 任意
- 500文字以内（推奨）

**completed:**
- 必須
- デフォルト: False

**user_id:**
- 必須
- 外部キー制約

### リレーションシップ

**User → Todo**
- 種類: 1対多（One to Many）
- カスケード削除: あり
- バックリファレンス: user

### インデックス

**複合インデックス:**
- `(user_id, completed)`: フィルター機能の高速化