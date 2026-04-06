'''
User Model
'''
from datetime import datetime, timezone
from flask_login import UserMixin  # is_authenticated 等のメソッドを自動で追加するミックスイン
from app import db, bcrypt         # db: SQLAlchemy インスタンス、bcrypt: パスワードハッシュ用


class User(UserMixin, db.Model):
    '''ユーザーモデル'''

    __tablename__ = 'users'  # DB のテーブル名を明示指定（省略すると 'user' になる）

    # カラム定義
    id = db.Column(db.Integer, primary_key=True)  # 主キー（自動採番）
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    # unique=True: 重複登録防止, nullable=False: 必須, index=True: 検索を高速化
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # メールアドレスも一意制約 + インデックス
    password_hash = db.Column(db.String(255), nullable=False)
    # 平文パスワードは保存しない。bcrypt ハッシュは約60文字だが余裕を持って255文字
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # default= でレコード挿入時に自動で現在時刻をセット（UTC タイムゾーン付き）
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)  # レコード更新時にも自動で現在時刻をセット
    )

    # リレーションシップ（後でTodoモデル作成後に有効化）
    # todos = db.relationship(
    #     'Todo',
    #     backref='user',
    #     lazy='dynamic',
    #     cascade='all, delete-orphan'
    # )

    def __repr__(self):
        # print(user) や デバッグ時に表示される文字列を定義
        return f'<User{self.username}>'

    def set_password(self, password):
        '''
        パスワードをハッシュ化して設定

        Args:
            password (str): 平文パスワード
        '''
        # bcrypt で不可逆ハッシュ化し、バイト列を UTF-8 文字列に変換して保存
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        '''
        パスワードを検証

        Args:
            password (str): 平文パスワード

        Returns:
            bool: パスワードが正しければTrue
        '''
        # 入力パスワードをハッシュして DB の password_hash と照合
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        '''
        辞書形式に変換

        Returns:
            dict: ユーザー情報（パスワードハッシュは除外）
        '''
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),   # ISO 8601 形式の文字列（JSON 化しやすい）
            'updated_at': self.updated_at.isoformat()
            # password_hash は意図的に含めない（セキュリティのため）
        }

    @staticmethod
    def find_by_username_or_email(identifier):
        '''
        ユーザー名またはメールアドレスでユーザーを検索

        Args:
            identifier (str): ユーザー名またはメールアドレス

        Returns:
            User: ユーザーオブジェクト（存在しない場合はNone）
        '''
        # db.or_() は SQL の OR 演算子に対応
        # 裏側で: SELECT * FROM users WHERE username = ? OR email = ? LIMIT 1
        return User.query.filter(
            db.or_(
                User.username == identifier,
                User.email == identifier
            )
        ).first()