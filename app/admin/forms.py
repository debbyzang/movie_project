# coding:utf8

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField, SelectField
from wtforms.validators import DataRequired, ValidationError
from app.modules import Admin, Tag

tags = Tag.query.all()


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


class MovieForm(FlaskForm):
    title = StringField(
        "片名",
        validators=[
            DataRequired("请输入片名")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片名！"
        }
    )
    url = FileField(
        "文件",
        validators=[
            DataRequired("请上传文件")
        ]
    )
    info = TextAreaField(
        "简介",
        validators=[
            DataRequired("请输入简介")
        ],
        render_kw={
            "class": "form-control",
            "rows": "10"
        }
    )
    logo = FileField(
        "封面",
        validators=[
            DataRequired("请上传封面")
        ]
    )
    star = SelectField(
        "星级",
        validators=[
            DataRequired("请选择星级")
        ],
        coerce=int,
        choices=[(1, "1星"),(2, "2星"),(3, "3星"),(4, "4星"),(5, "5星")],
        render_kw={
            "class": "form-control",
            "id": "input_star"
        }
    )
    tag_id = SelectField(
        "标签",
        validators=[
            DataRequired("请选择标签")
        ],
        coerce=int,
        choices=[(v.id, v.name) for v in tags],
        render_kw={
            "class": "form-control",
            "id": "input_star"
        }
    )
    area = StringField(
        "地区",
        validators=[
            DataRequired("请输入地区")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入地区！"
        }
    )

    length = StringField(
        "片长",
        validators=[
            DataRequired("请输入片长")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请输入片长！"
        }
    )
    release_time = StringField(
        "上映时间",
        validators=[
            DataRequired("请选择上映时间")
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "请选择上映时间！",
            "id":"input_release_time"
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

