'''
Todos Blueprint - スケルトン（詳細は Week 3 Day 3 で実装）
'''
from flask import Blueprint

todos_bp = Blueprint('todos', __name__)


@todos_bp.route('/')
def index():
    '''ToDoリスト（Week 3 Day 3 で詳細実装予定）'''
    return {'message': 'TODO: implement'}, 200