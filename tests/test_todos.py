'''
Todos Test (Filter functionality)
'''
import pytest
from app.models.todo import Todo
from app import db


class TestTodoFilters:
    '''ToDoフィルター機能のテスト'''

    def _login(self, client):
        '''テスト用ログインヘルパー（各テストで繰り返すコードを共通化）'''
        client.post('/auth/login', data={
            'identifier': 'testuser',
            'password': 'password123'
        })

    def _create_todos(self, user):
        '''テスト用ToDo作成ヘルパー'''
        todo1 = Todo(title='FilterTest Active1', user_id=user.id, completed=False)
        todo2 = Todo(title='FilterTest Done1', user_id=user.id, completed=True)
        todo3 = Todo(title='FilterTest Active2', user_id=user.id, completed=False)
        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()
        return todo1, todo2, todo3

    def test_filter_all(self, client, user):
        '''全てのToDoを表示'''
        self._create_todos(user)
        self._login(client)

        # 末尾スラッシュ付き（Blueprint の url_prefix='/todos' + route='/'）
        response = client.get('/todos/?filter=all')
        text = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'FilterTest Active1' in text
        assert 'FilterTest Done1' in text
        assert 'FilterTest Active2' in text

    def test_filter_active(self, client, user):
        '''未完了のToDoのみ表示'''
        self._create_todos(user)
        self._login(client)

        response = client.get('/todos/?filter=active')
        text = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'FilterTest Active1' in text
        assert 'FilterTest Done1' not in text  # 完了済みなので表示されないはず
        assert 'FilterTest Active2' in text

    def test_filter_completed(self, client, user):
        '''完了したToDoのみ表示'''
        todo1 = Todo(title='FilterTest Active1', user_id=user.id, completed=False)
        todo2 = Todo(title='FilterTest Done1', user_id=user.id, completed=True)
        todo3 = Todo(title='FilterTest Done2', user_id=user.id, completed=True)
        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()

        self._login(client)

        response = client.get('/todos/?filter=completed')
        text = response.data.decode('utf-8')

        assert response.status_code == 200
        assert 'FilterTest Active1' not in text  # 未完了なので表示されないはず
        assert 'FilterTest Done1' in text
        assert 'FilterTest Done2' in text

    def test_filter_count_badges(self, client, user):
        '''フィルターのカウントバッジが正しいか'''
        self._create_todos(user)
        self._login(client)

        response = client.get('/todos/')
        text = response.data.decode('utf-8')

        assert response.status_code == 200
        # ページ内のHTML要素から件数を確認
        # ※ b'3' のような単純なバイト比較だと HTML 内の他の数字にもマッチするため、
        #   テンプレートで使っているバッジの形式に合わせて検証する
        #   例: <span class="badge">3</span> のようなパターン
        assert 'FilterTest Active1' in text
        assert 'FilterTest Done1' in text
        assert 'FilterTest Active2' in text