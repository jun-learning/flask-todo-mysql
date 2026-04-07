'''
Models Test
'''
import pytest
from app.models.user import User
from app.models.todo import Todo
from app import db


class TestUserModel:
    '''Userモデルのテスト'''

    def test_create_user(self, app):
        '''ユーザー作成テスト'''
        user = User(
            username='newuser',
            email='newuser@example.com'
        )
        user.set_password('password123')

        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.password_hash is not None
        assert user.password_hash != 'password123'

    def test_password_hashing(self, app):
        '''パスワードハッシュ化テスト'''
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')

        assert user.password_hash != 'password123'
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')

    def test_unique_username(self, app, user):
        '''ユーザー名の一意制約テスト'''
        duplicate_user = User(
            username='testuser',  # 既存のユーザー名
            email='another@example.com'
        )
        duplicate_user.set_password('password123')

        db.session.add(duplicate_user)

        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()

    def test_unique_email(self, app, user):
        '''メールアドレスの一意制約テスト'''
        duplicate_user = User(
            username='anotheruser',
            email='test@example.com'  # 既存のメールアドレス
        )
        duplicate_user.set_password('password123')

        db.session.add(duplicate_user)

        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()

    def test_find_by_username_or_email(self, app, user):
        '''ユーザー名・メールアドレス検索テスト'''
        # ユーザー名で検索
        found_user = User.find_by_username_or_email('testuser')
        assert found_user is not None
        assert found_user.id == user.id

        # メールアドレスで検索
        found_user = User.find_by_username_or_email('test@example.com')
        assert found_user is not None
        assert found_user.id == user.id

        # 存在しないユーザー
        found_user = User.find_by_username_or_email('nonexistent')
        assert found_user is None

    def test_to_dict(self, app, user):
        '''辞書変換テスト'''
        user_dict = user.to_dict()

        assert user_dict['id'] == user.id
        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert 'password_hash' not in user_dict
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict


class TestTodoModel:
    '''Todoモデルのテスト'''

    def test_create_todo(self, app, user):
        '''ToDo作成テスト'''
        todo = Todo(
            title='New Todo',
            description='Description',
            user_id=user.id
        )

        db.session.add(todo)
        db.session.commit()

        assert todo.id is not None
        assert todo.title == 'New Todo'
        assert todo.description == 'Description'
        assert todo.completed is False   # デフォルトは未完了であることを確認
        assert todo.user_id == user.id

    def test_todo_user_relationship(self, app, user, todo):
        '''User-Todoリレーションシップテスト'''
        # ToDoからUserを参照（backref='user' で設定）
        assert todo.user.id == user.id
        assert todo.user.username == 'testuser'

        # UserからToDoを参照（lazy='dynamic' なので .all() が必要）
        user_todos = user.todos.all()
        assert len(user_todos) == 1
        assert user_todos[0].id == todo.id

    def test_toggle_completed(self, app, todo):
        '''完了状態切り替えテスト'''
        # 初期状態：未完了
        assert todo.completed is False

        # 完了に切り替え
        result = todo.toggle_completed()
        assert result is True
        assert todo.completed is True

        # 未完了に切り替え
        result = todo.toggle_completed()
        assert result is False
        assert todo.completed is False

    def test_get_user_todos_all(self, app, user):
        '''全てのToDo取得テスト'''
        # 複数のToDoを作成
        todo1 = Todo(title='Todo 1', user_id=user.id, completed=False)
        todo2 = Todo(title='Todo 2', user_id=user.id, completed=True)
        todo3 = Todo(title='Todo 3', user_id=user.id, completed=False)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()

        # 全て取得
        todos = Todo.get_user_todos(user.id, 'all')
        assert len(todos) == 3

    def test_get_user_todos_active(self, app, user):
        '''未完了のToDo取得テスト'''
        # 複数のToDoを作成
        todo1 = Todo(title='Todo 1', user_id=user.id, completed=False)
        todo2 = Todo(title='Todo 2', user_id=user.id, completed=True)
        todo3 = Todo(title='Todo 3', user_id=user.id, completed=False)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()

        # 未完了のみ取得
        todos = Todo.get_user_todos(user.id, 'active')
        assert len(todos) == 2
        assert all(not todo.completed for todo in todos)

    def test_get_user_todos_completed(self, app, user):
        '''完了したToDo取得テスト'''
        # 複数のToDoを作成
        todo1 = Todo(title='Todo 1', user_id=user.id, completed=False)
        todo2 = Todo(title='Todo 2', user_id=user.id, completed=True)
        todo3 = Todo(title='Todo 3', user_id=user.id, completed=True)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()

        # 完了のみ取得
        todos = Todo.get_user_todos(user.id, 'completed')
        assert len(todos) == 2
        assert all(todo.completed for todo in todos)

    def test_count_user_todos(self, app, user):
        '''ToDo数カウントテスト'''
        # 複数のToDoを作成
        todo1 = Todo(title='Todo 1', user_id=user.id, completed=False)
        todo2 = Todo(title='Todo 2', user_id=user.id, completed=True)
        todo3 = Todo(title='Todo 3', user_id=user.id, completed=False)

        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()

        # カウント
        assert Todo.count_user_todos(user.id, 'all') == 3
        assert Todo.count_user_todos(user.id, 'active') == 2
        assert Todo.count_user_todos(user.id, 'completed') == 1

    def test_cascade_delete(self, app, user, todo):
        '''カスケード削除テスト'''
        todo_id = todo.id

        # ユーザーを削除
        db.session.delete(user)
        db.session.commit()

        # ToDoも削除されているか確認（cascade='all, delete-orphan' の効果）
        deleted_todo = db.session.get(Todo, todo_id)
        assert deleted_todo is None

    def test_to_dict(self, app, todo):
        '''辞書変換テスト'''
        todo_dict = todo.to_dict()

        assert todo_dict['id'] == todo.id
        assert todo_dict['title'] == 'Test Todo'
        assert todo_dict['description'] == 'Test Description'
        assert todo_dict['completed'] is False
        assert todo_dict['user_id'] == todo.user_id
        assert 'created_at' in todo_dict
        assert 'updated_at' in todo_dict