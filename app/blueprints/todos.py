'''
Todos Blueprint
'''
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user  # ログイン状態の管理
from app import db
from app.models.todo import Todo
from app.forms.todo_forms import TodoForm, TodoToggleForm

todos_bp = Blueprint('todos', __name__)


@todos_bp.route('/')
@login_required  # 未ログインなら自動的にログインページへリダイレクト
def index():
    '''ToDoリスト'''
    # URL クエリパラメータからフィルタータイプを取得（?filter=active 等）
    # デフォルトは 'all'（全件表示）
    filter_type = request.args.get('filter', 'all')

    # ToDoリスト取得（現在ログイン中のユーザーの ToDo のみ）
    todos = Todo.get_user_todos(current_user.id, filter_type)

    # フィルタータブのカウントバッジ用に各件数を取得
    counts = {
        'all': Todo.count_user_todos(current_user.id, 'all'),
        'active': Todo.count_user_todos(current_user.id, 'active'),
        'completed': Todo.count_user_todos(current_user.id, 'completed')
    }

    # 完了切り替えフォーム（CSRF トークン生成のために作成）
    toggle_form = TodoToggleForm()

    return render_template(
        'todos/list.html',
        todos=todos,
        filter_type=filter_type,
        counts=counts,
        toggle_form=toggle_form
    )


@todos_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    '''ToDo新規作成'''
    form = TodoForm()

    if form.validate_on_submit():
        # バリデーション通過 → フォームデータから ToDo を作成
        todo = Todo(
            title=form.title.data,
            description=form.description.data,
            user_id=current_user.id  # 現在のログインユーザーに紐づける
        )

        try:
            db.session.add(todo)    # セッションに追加（まだ DB には書かれない）
            db.session.commit()     # DB に確定書き込み

            flash('ToDoを作成しました。', 'success')
            # PRG パターン: 作成後は一覧ページにリダイレクト（リロードで二重作成を防ぐ）
            return redirect(url_for('todos.index'))

        except Exception as e:
            db.session.rollback()   # 失敗したらセッションを元に戻す
            flash('ToDoの作成に失敗しました。', 'error')

    # GET リクエストまたはバリデーション失敗時: フォームを表示
    return render_template('todos/new.html', form=form)


@todos_bp.route('/<int:id>')
@login_required
def show(id):
    '''ToDo詳細'''
    # get_or_404: id のレコードが存在しなければ 404 エラーを返す
    todo = Todo.query.get_or_404(id)

    # 所有者チェック: 他人の ToDo にアクセスしようとしたら 403 エラー
    if todo.user_id != current_user.id:
        abort(403)

    return render_template('todos/detail.html', todo=todo)


@todos_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    '''ToDo編集'''
    todo = Todo.query.get_or_404(id)  # 存在しない id なら 404 エラー

    # 所有者チェック: 他人の ToDo を編集しようとしたら 403 エラー
    if todo.user_id != current_user.id:
        abort(403)

    # obj=todo を渡すと、フォームの初期値に既存データが入力される
    form = TodoForm(obj=todo)

    if form.validate_on_submit():
        # バリデーション通過 → フォームデータで ToDo を更新
        todo.title = form.title.data
        todo.description = form.description.data
        # updated_at は onupdate=lambda: datetime.now(timezone.utc) で自動更新される

        try:
            db.session.commit()  # add() は不要（既存オブジェクトの変更は自動追跡される）

            flash('ToDoを更新しました。', 'success')
            return redirect(url_for('todos.show', id=todo.id))

        except Exception as e:
            db.session.rollback()
            flash('ToDoの更新に失敗しました。', 'error')

    return render_template('todos/edit.html', form=form, todo=todo)


@todos_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    '''ToDo削除'''
    # 実装は後で
    flash('削除機能は次のステップで実装します', 'info')
    return redirect(url_for('todos.index'))


@todos_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
def toggle(id):
    '''完了/未完了切り替え'''
    # 実装は後で
    flash('切り替え機能は次のステップで実装します', 'info')
    return redirect(url_for('todos.index'))