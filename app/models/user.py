'''
User Model
'''
from datetime import datetime, timezone
from flask_login import UserMixin
from app import db, bcrypt


class User(UserMixin, db.Model):
    '''ユーザーモデル'''

    __tablename__ = 'users'

    # カラム定義
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # リレーションシップ（追加）
    todos = db.relationship(
        'Todo',
        backref='user',              # todo.user で所有ユーザーにアクセスできる（Todo 側への逆参照）
        lazy='dynamic',              # user.todos はクエリオブジェクトを返す（.filter_by() 等が使える）
        cascade='all, delete-orphan' # ユーザー削除時に紐づく ToDo も自動削除
    )

    def __repr__(self):
        return f'<User{self.username}>'

    def set_password(self, password):
        '''
        パスワードをハッシュ化して設定

        Args:
            password (str): 平文パスワード
        '''
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        '''
        パスワードを検証

        Args:
            password (str): 平文パスワード

        Returns:
            bool: パスワードが正しければTrue
        '''
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
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
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
        return User.query.filter(
            db.or_(
                User.username == identifier,
                User.email == identifier
            )
        ).first()