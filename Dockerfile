# ベースイメージ: Python 3.11 の最小構成（slim = 不要なパッケージを含まない軽量版）
FROM python:3.11-slim

# 作業ディレクトリ設定: 以降の命令はこのディレクトリ内で実行される
WORKDIR /app

# システムパッケージインストール: PyMySQL が MySQL に接続するために必要なライブラリ
# && でコマンドをつなぎ、最後に apt キャッシュを削除してイメージサイズを削減
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# PYTHONUNBUFFERED=1: Python の出力バッファリングを無効化
# → docker compose logs でリアルタイムにログが表示されるようになる
ENV PYTHONUNBUFFERED=1

# requirements.txt だけを先にコピー（キャッシュ効率化のポイント）
# アプリコードが変わっても requirements.txt が変わらなければ pip install のキャッシュが使える
COPY requirements.txt .

# 依存パッケージインストール（--no-cache-dir でpipキャッシュを保存しない → イメージサイズ削減）
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコード全体をコピー（コード変更時はここからやり直し）
# requirements.txt より後に書くことで、コード変更時でも pip install をスキップできる
COPY . .

# コンテナが使うポートを宣言（ドキュメント的な意味。実際の公開は docker-compose.yml で設定）
EXPOSE 5000

# コンテナ起動時のデフォルトコマンド（docker-compose.yml の command で上書き可能）
CMD ["python", "run.py"]