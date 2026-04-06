.PHONY: help build up down restart logs shell db-shell test clean

# ヘルプ: ## に続くコメントを自動で一覧表示する
help: ## このヘルプを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

build: ## Docker イメージをビルド
	docker compose build

up: ## コンテナを起動
	docker compose up -d

down: ## コンテナを停止
	docker compose down

restart: ## コンテナを再起動
	docker compose restart

logs: ## ログを表示
	docker compose logs -f

shell: ## アプリケーションコンテナのシェルに入る
	docker compose exec app bash

db-shell: ## MySQLシェルに入る
	docker compose exec db mysql -u root -prootpassword flask_todo

test: ## テストを実行
	docker compose exec app pytest

test-cov: ## カバレッジ付きでテストを実行
	docker compose exec app pytest --cov=app --cov-report=html

format: ## コードをフォーマット
	docker compose exec app black app/ tests/

lint: ## リンターを実行
	docker compose exec app flake8 app/ tests/

clean: ## ボリュームも含めて完全削除
	docker compose down -v
	rm -rf migrations/

init-db: ## データベースを初期化
	docker compose exec app flask db init
	docker compose exec app flask db migrate -m "Initial migration"
	docker compose exec app flask db upgrade

reset-db: ## データベースをリセット
	./scripts/reset_db.sh