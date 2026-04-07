'''
Todo Model
'''
from datetime import datetime, timezone
from app import db


class Todo(db.Model):
    '''ToDoモデル'''

    __tablename__ = 'todos'

    # カラム定義
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)          # タイトル（必須、最大100文字）
    description = db.Column(db.Text, nullable=True)            # 説明（任意）
    completed = db.Column(db.Boolean, nullable=False, default=False)  # 完了フラグ（デフォルトは未完了）
    # models/todo.py 内の user_id カラム
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # user_id は users テーブルの id を参照する外部キー（必須）
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # レコード作成時刻（UTC で自動設定）
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)  # 更新時も自動で現在時刻をセット
    )

    # インデックス
    __table_args__ = (
        # user_id と completed の複合インデックス：フィルター機能の検索を高速化する
        db.Index('ix_todos_user_id_completed', 'user_id', 'completed'),
    )

    def __repr__(self):
        return f'<Todo{self.title}>'

    def toggle_completed(self):
        '''
        完了状態を切り替え

        Returns:
            bool: 新しい完了状態
        '''
        self.completed = not self.completed  # True → False、False → True のトグル
        return self.completed

    def to_dict(self):
        '''
        辞書形式に変換（API レスポンスや JSON 出力に使用）

        Returns:
            dict: ToDo情報
        '''
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),   # ISO 8601 形式の文字列に変換
            'updated_at': self.updated_at.isoformat()
        }

    @staticmethod
    def get_user_todos(user_id, filter_type='all'):
        '''
        ユーザーのToDoリストを取得

        Args:
            user_id (int): ユーザーID
            filter_type (str): フィルタータイプ（'all', 'active', 'completed'）

        Returns:
            list: ToDoリスト
        '''
        # まず指定ユーザーの ToDo だけに絞り込む
        # SQL: SELECT * FROM todos WHERE user_id = {user_id}
        query = Todo.query.filter_by(user_id=user_id)

        if filter_type == 'active':
            # 未完了のみ追加フィルター
            query = query.filter_by(completed=False)
        elif filter_type == 'completed':
            # 完了済みのみ追加フィルター
            query = query.filter_by(completed=True)

        # 作成日時の降順（新しいものが上）で全件取得
        return query.order_by(Todo.created_at.desc()).all()

    @staticmethod
    def count_user_todos(user_id, filter_type='all'):
        '''
        ユーザーのToDo数をカウント

        Args:
            user_id (int): ユーザーID
            filter_type (str): フィルタータイプ（'all', 'active', 'completed'）

        Returns:
            int: ToDo数
        '''
        query = Todo.query.filter_by(user_id=user_id)

        if filter_type == 'active':
            query = query.filter_by(completed=False)
        elif filter_type == 'completed':
            query = query.filter_by(completed=True)

        # .all() ではなく .count() でカウントのみ取得（SQL: SELECT COUNT(*) ...）
        return query.count()