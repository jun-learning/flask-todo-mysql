'''
Todo Forms
'''
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class TodoForm(FlaskForm):
    '''ToDo作成・編集フォーム'''

    title = StringField(
        'タイトル',
        validators=[
            DataRequired(message='タイトルは必須です'),           # 空欄を禁止
            Length(min=1, max=100, message='タイトルは1〜100文字で入力してください')
        ]
    )

    description = TextAreaField(
        '説明',
        validators=[
            Length(max=500, message='説明は500文字以内で入力してください')
            # DataRequired がないため、空欄でもOK（任意フィールド）
        ]
    )

    submit = SubmitField('保存')


class TodoToggleForm(FlaskForm):
    '''完了/未完了切り替えフォーム（CSRF保護のみ）'''
    # フィールドは不要だが、FlaskForm を継承することで CSRF トークン検証が自動的に行われる
    pass