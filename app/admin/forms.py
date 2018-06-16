# coding:utf8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, ValidationError
from app.modules import Admin


class LoginForm(FlaskForm):
    account = StringField(
        "账号",
        validators=[
            DataRequired(message="请输入账号"),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入账号！",
        }
    )

    pwd = PasswordField(
        "密码",
        validators=[
            DataRequired(message="请输入密码"),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入密码！",
        }
    )

    submit = SubmitField(
        "提交",
        render_kw={
            "class": "btn btn-primary btn-block btn-flat"
        }
    )

    def validate_account(self, field):
        account = field.data
        admin = Admin.query.filter_by(name=account).count()
        if admin == 0:
            raise ValidationError('账号不存在')


class TagForm(FlaskForm):
    name = StringField(
        '标签',
        description='请输入标签',
        validators=[
            DataRequired("请输入标签！")
        ],
        render_kw={
            "class": "form-control",
            "id": "input_name",
            "placeholder": "请输入标签名称！",

        }
    )

    submit = SubmitField(
        "添加",
        render_kw={
            "class": "btn btn-primary"

        }
    )
    edit = SubmitField(
        "编辑",
        render_kw={
            "class": "btn btn-primary"

        }
    )
