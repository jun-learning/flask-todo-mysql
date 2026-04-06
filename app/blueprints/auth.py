'''
Auth Blueprint
'''
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
# login_user: ユーザーをログイン状態にしてセッションに保存
# logout_user: セッションからユーザー情報を削除
# current_user: 現在ログイン中のユーザー（未ログインなら AnonymousUser）
from app import db
from app.models.user import User
from app.forms.auth_forms import SignupForm, LoginForm

auth_bp = Blueprint('auth', __name__)  # 'auth' という名前の Blueprint


@auth_bp.route('/signup', methods=['GET', 'POST'])
# GET: フォームを表示、POST: フォームの送信を処理
def signup():
    '''ユーザー登録'''
    # 既にログイン済みの場合はToDoリストへリダイレクト
    if current_user.is_authenticated:
        return redirect(url_for('todos.index'))

    form = SignupForm()  # フォームインスタンスを作成（POST データは自動で読み込まれる）

    if form.validate_on_submit():
        # POST リクエストかつ全バリデーション通過の場合
        user = User(
            username=form.username.data,  # フォームの入力値を取得
            email=form.email.data
        )
        user.set_password(form.password.data)  # パスワードをハッシュ化して設定

        # データベースに保存
        try:
            db.session.add(user)    # セッションに追加
            db.session.commit()     # DB にコミット

            flash('ユーザー登録が完了しました。ログインしてください。', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()   # エラー時はロールバックして DB を元の状態に戻す
            flash('ユーザー登録に失敗しました。もう一度お試しください。', 'error')
            return render_template('auth/signup.html', form=form)

    # GET リクエスト、またはバリデーション失敗時はフォームを再表示
    return render_template('auth/signup.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    '''ログイン'''
    if current_user.is_authenticated:
        return redirect(url_for('todos.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # ユーザー名またはメールアドレスでユーザーを検索
        user = User.find_by_username_or_email(form.identifier.data)

        # ユーザーが存在し、パスワードが正しい場合
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            # remember=True の場合、ブラウザを閉じてもログイン状態が維持される

            # ログイン前にアクセスしようとしていたページがあれば、そこへリダイレクト
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            flash(f'ようこそ、{user.username}さん！', 'success')
            return redirect(url_for('todos.index'))

        # 認証失敗（セキュリティのため「ユーザー名が存在しない」「パスワードが違う」を区別しない）
        flash('ユーザー名またはパスワードが正しくありません。', 'error')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    '''ログアウト'''
    logout_user()  # セッションからユーザー情報を削除
    flash('ログアウトしました。', 'info')
    return redirect(url_for('main.index'))