'''
Todos Blueprint
'''
from flask import Blueprint, render_template
from flask_login import login_required, current_user
# login_required: 未ログインユーザーをログインページへリダイレクトするデコレータ
# current_user: 現在ログイン中のユーザーオブジェクト

todos_bp = Blueprint('todos', __name__)


@todos_bp.route('/')
@login_required  # ログインしていないと /auth/login へリダイレクト
def index():
    '''ToDoリスト（Week 3 で詳細実装予定）'''
    return render_template('todos/list.html')