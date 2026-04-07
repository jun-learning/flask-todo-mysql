'''
Gunicorn設定ファイル
Python ファイルとして書けるため、multiprocessing モジュールを使った動的な値設定が可能
'''
import multiprocessing
import os

# ========== サーバーソケット設定 ==========
# bind: 待ち受けるアドレスとポートの組み合わせ
# '0.0.0.0' は全てのネットワークインターフェースで待ち受け（Docker コンテナ内では必須）
bind = '0.0.0.0:8000'

# backlog: 待機中の接続キューの最大数
# 高負荷時に接続を一時的にキューに積む。通常は 2048 で十分
backlog = 2048

# ========== ワーカープロセス設定 ==========
# workers: 起動するワーカープロセス数
# 推奨値: CPU コア数 × 2 + 1（I/O 待ちが多い Web アプリ向けの経験則）
workers = multiprocessing.cpu_count() * 2 + 1

# worker_class: ワーカーの処理モデル
# 'sync'  : 同期処理（デフォルト）。CPU バウンドな処理に適している
# 'gevent': コルーチン方式。大量の同時接続や I/O 待ちが多い場合に有効
# 'gthread': スレッドプール方式。sync と gevent の中間
worker_class = 'sync'

# worker_connections: gevent/eventlet 使用時の最大同時接続数
# sync ワーカーでは無効だが、将来 gevent に切り替える際の設定として記述
worker_connections = 1000

# max_requests: ワーカーが処理するリクエスト数の上限
# この数に達したらワーカーを再起動してメモリリークを防ぐ
max_requests = 1000

# max_requests_jitter: max_requests にランダムなばらつきを追加
# 全ワーカーが同時に再起動するのを防ぐ（例: 950〜1050 でランダムに再起動）
max_requests_jitter = 50

# timeout: この秒数を超えてもレスポンスがないワーカーを強制終了（秒）
# 重い処理がある場合は延ばす（例: ファイルアップロードなら 120 秒）
timeout = 30

# keepalive: Keep-Alive 接続を維持する秒数
# Nginx がリバースプロキシの場合は 2〜5 秒が推奨
keepalive = 2

# ========== デバッグ設定 ==========
# reload: コードが変更されたら自動的にワーカーを再起動する
# 環境変数 FLASK_DEBUG が '1' のときだけ有効にする（本番は False）
reload = os.getenv('FLASK_DEBUG') == '1'

# reload_engine: ファイル変更の監視方法（'auto' で OS に合わせて自動選択）
reload_engine = 'auto'

# ========== ロギング設定 ==========
# accesslog: アクセスログの出力先
# '-' は標準出力（Docker では `docker compose logs` で確認できる）
accesslog = '-'  # stdout

# errorlog: エラーログの出力先（'-' で標準エラー出力）
errorlog = '-'   # stderr

# loglevel: ログレベル（debug / info / warning / error / critical）
loglevel = 'info'

# access_log_format: アクセスログのフォーマット（Apache のログ形式に準拠）
# %(h)s: クライアント IP、%(r)s: リクエスト行、%(s)s: ステータスコード、%(D)s: 処理時間（マイクロ秒）
access_log_format = '%(h)s%(l)s%(u)s%(t)s "%(r)s"%(s)s%(b)s "%(f)s" "%(a)s"%(D)s'

# ========== プロセス名 ==========
# ps コマンドで表示されるプロセス名（サーバー上で識別しやすくなる）
proc_name = 'flask_todo_app'

# ========== サーバーメカニクス ==========
# daemon: バックグラウンドプロセスとして実行するか
# Docker コンテナ内では False（フォアグラウンドで動かす必要がある）
daemon = False

# pidfile: PID ファイルのパス（None で無効）
# systemd で管理する場合に使う。Docker では不要
pidfile = None

# umask: 作成ファイルのパーミッションマスク（0 = デフォルト）
umask = 0

# user / group: ワーカープロセスを実行するユーザー/グループ
# None は実行ユーザーのまま（本番では専用ユーザーを指定するのが推奨）
user = None
group = None

# tmp_upload_dir: 一時ファイルのアップロードディレクトリ（None でデフォルト）
tmp_upload_dir = None

# ========== セキュリティ設定 ==========
# limit_request_line: リクエスト行の最大バイト数（URL の長さ制限）
limit_request_line = 4096

# limit_request_fields: リクエストヘッダーの最大フィールド数
limit_request_fields = 100

# limit_request_field_size: 各ヘッダーフィールドの最大バイト数
limit_request_field_size = 8190