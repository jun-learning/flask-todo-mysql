'''
Auth Blueprint - スケルトン（詳細は Week 2 Day 4 で実装）
'''
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    '''ユーザー登録（Week 2 Day 4 で詳細実装予定）'''
    return {'message': 'TODO: implement'}, 200


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''ログイン（Week 2 Day 4 で詳細実装予定）'''
    return {'message': 'TODO: implement'}, 200


@auth_bp.route('/logout')
def logout():
    '''ログアウト（Week 2 Day 4 で詳細実装予定）'''
    return {'message': 'TODO: implement'}, 200