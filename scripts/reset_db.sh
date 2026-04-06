#!/bin/bash

echo '===== Database Reset Script ====='

# コンテナが起動しているか確認
if ! docker compose ps | grep -q 'db'; then
    echo 'Error: Database container is not running'
    exit 1
fi

# データベース削除
echo 'Dropping database...'
# セキュリティ注意: パスワードをコマンドライン引数に直接書くとプロセス一覧に表示されます
# 本番環境では MYSQL_PWD 環境変数や ~/.my.cnf を使う方が安全です
docker compose exec db mysql -u root -prootpassword -e "DROP DATABASE IF EXISTS flask_todo;"

# データベース再作成
echo 'Creating database...'
docker compose exec db mysql -u root -prootpassword -e "CREATE DATABASE flask_todo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 権限付与
echo 'Granting privileges...'
docker compose exec db mysql -u root -prootpassword -e "GRANT ALL PRIVILEGES ON flask_todo.* TO 'flaskuser'@'%'; FLUSH PRIVILEGES;"

# マイグレーション実行
echo 'Running migrations...'
docker compose exec app flask db upgrade

echo '===== Database Reset Completed ====='