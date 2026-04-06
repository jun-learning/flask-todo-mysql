-- データベース初期化スクリプト
-- MySQL コンテナの初回起動時に自動実行される

-- 文字コード設定: 日本語や絵文字（emoji）を正しく扱うために utf8mb4 を使用
ALTER DATABASE flask_todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- テスト用データベース作成（テスト実行時に本番DBを汚さないため分離）
CREATE DATABASE IF NOT EXISTS flask_todo_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 権限付与: flaskuser が flask_todo と flask_todo_test にアクセスできるようにする
-- '%' はどのホストからの接続も許可（コンテナ間通信に必要）
GRANT ALL PRIVILEGES ON flask_todo.* TO 'flaskuser'@'%';
GRANT ALL PRIVILEGES ON flask_todo_test.* TO 'flaskuser'@'%';
FLUSH PRIVILEGES;  -- 権限変更を即座に反映