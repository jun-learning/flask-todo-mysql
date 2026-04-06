'''
Main Blueprint - スケルトン（詳細は Week 2 Day 4 で実装）
'''
from flask import Blueprint

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    '''トップページ（Week 2 Day 4 で詳細実装予定）'''
    return {'message': 'TODO: implement'}, 200


@main_bp.route('/health')
def health():
    '''ヘルスチェック'''
    return {'status': 'healthy'}, 200