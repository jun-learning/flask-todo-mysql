'''
Main Blueprint
'''
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)  # 'main' は Blueprint の名前（url_for('main.index') のように使う）


@main_bp.route('/')  # ルートパス（/）にアクセスしたときに実行
def index():
    '''トップページ'''
    return render_template('index.html')


@main_bp.route('/health')  # ヘルスチェック用エンドポイント（Docker の healthcheck で使う）
def health():
    '''ヘルスチェック'''
    return {'status': 'healthy'}, 200