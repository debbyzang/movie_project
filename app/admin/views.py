# coding:utf-8

from . import admin
from flask import url_for, render_template, redirect, flash, request, session
from app.admin.forms import LoginForm, TagForm, MovieForm, PreviewForm
from app.modules import Admin, Tag, Movie, db, Preview, User, Comment, Moviecol
from app import app
from functools import wraps
from werkzeug.utils import secure_filename
import os, uuid, datetime, stat


# 登录装饰器
def admin_login_req(f):
    @wraps(f)
    def decoreated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)

    return decoreated_function


# 修改文件名
def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    # todo file suffix name confused
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex) + "." + fileinfo[0]
    return filename


@admin.route("/")
@admin_login_req
def index():
    return render_template("admin/index.html")


@admin.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        admin = Admin.query.filter_by(name=data["account"]).first()
        if not admin.check_pwd(data["pwd"]):
            flash("密码错误")
            return redirect(url_for("admin.login"))
        session['admin'] = data['account']
        return redirect(url_for("admin.index"))
        # return redirect(request.args.get("next") or url_for("admin.login"))
    return render_template("admin/login.html", form=form)


@admin.route("/logout/")
@admin_login_req
def logout():
    session.pop('admin', None)
    return redirect(url_for("admin.login"))


@admin.route("/pwd/")
@admin_login_req
def pwd():
    return render_template("admin/pwd.html")


# 添加标签
@admin.route("/tag/add", methods=["GET", "POST"])
@admin_login_req
def tag_add():
    form = TagForm()
    if form.validate_on_submit():
        data = form.data
        tag = Tag.query.filter_by(name=data['name']).count()
        if tag >= 1:
            flash("标签已存在", "err")
            return redirect(url_for("admin.tag_add"))
        tag = Tag(
            name=data['name']
        )
        db.session.add(tag)
        db.session.commit()
        flash("添加标签成功", "ok")
        redirect(url_for("admin.tag_add"))
    return render_template("admin/tag_add.html", form=form)


# 编辑标签
@admin.route("/tag/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def tag_edit(id):
    form = TagForm()
    tag = Tag.query.get_or_404(id)
    # page_data = Tag.query.order_by(
    #     Tag.addtime.desc()
    # ).paginate(page=1, per_page=10)
    if form.validate_on_submit():
        data = form.data
        tag_count = Tag.query.filter_by(name=data['name']).count()
        if tag_count >= 1:
            flash("标签已存在", "err")
            return redirect(url_for("admin.tag_edit", id=id))
        tag.name = data['name']
        db.session.add(tag)
        db.session.commit()
        flash("修改标签成功", "ok")
        # 想做成跳转到list页面，不知道怎么弄
        redirect(url_for("admin.tag_list", page=1))
        # redirect(url_for("admin.tag_edit", id=id))
    return render_template("admin/tag_edit.html", form=form, tag=tag)


# 标签列表
@admin.route("/tag/list/<int:page>/", methods=["GET"])
@admin_login_req
def tag_list(page):
    if page is None:
        page = 1
    page_data = Tag.query.order_by(
        Tag.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/tag_list.html", page_data=page_data)


# 删除标签
@admin.route("/tag/del/<int:id>/", methods=["GET"])
@admin_login_req
def tag_del(id=None):
    tag = Tag.query.filter_by(id=id).first_or_404()
    db.session.delete(tag)
    db.session.commit()
    flash("标签删除成功", "ok")
    return redirect(url_for("admin.tag_list", page=1))


# 添加电影
@admin.route("/movie/add", methods=["GET", "POST"])
def movie_add():
    form = MovieForm()
    if form.validate_on_submit():
        data = form.data
        file_url = secure_filename(form.url.data.filename)
        print("***********")
        print("file_url " + file_url)
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)
        url = change_filename(file_url)
        print("url " + url)
        logo = change_filename(file_logo)
        form.url.data.save(app.config["UP_DIR"] + url)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        movie = Movie(
            title=data['title'],
            url=url,
            info=data['info'],
            logo=logo,
            star=int(data['star']),
            playnum=0,
            commentnum=0,
            tag_id=int(data['tag_id']),
            area=data['area'],
            release_time=data['release_time'],
            length=data['length']
        )
        db.session.add(movie)
        db.session.commit()
        flash("添加电影成功", "ok")
        return redirect(url_for("admin.movie_add"))
    return render_template("admin/movie_add.html", form=form)


# 电影列表
@admin.route("/movie/list/<int:page>", methods=["GET"])
@admin_login_req
def movie_list(page=None):
    if page == None:
        page = 1
    page_data = Movie.query.join(Tag).filter(
        Tag.id == Movie.tag_id
    ).order_by(
        Movie.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/movie_list.html", page_data=page_data)


# 删除电影
@admin.route("/movie/del/<int:id>/", methods=["GET"])
@admin_login_req
def movie_del(id=None):
    movie = Movie.query.get_or_404(int(id))
    db.session.delete(movie)
    db.session.commit()
    flash("电影删除成功", "ok")
    return redirect(url_for("admin.movie_list", page=1))


# 编辑电影
@admin.route("/movie/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def movie_edit(id):
    form = MovieForm()
    movie = Movie.query.get_or_404(int(id))
    form.url.validators = []
    form.logo.validators = []
    if request.method == "GET":
        form.info.data = movie.info
        form.tag_id.data = movie.tag_id
        form.star.data = movie.star
    if form.validate_on_submit():
        data = form.data
        movie_count = Movie.query.filter_by(title=data['title']).count()
        if movie_count >= 1 and movie.title != data['title']:
            flash("片名已存在", "err")
            return redirect(url_for("admin.movie_edit", id=movie.id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        if form.url.data != "":
            file_url = secure_filename(form.url.data.filename)
            movie.url = change_filename(file_url)
            form.url.data.save(app.config["UP_DIR"] + movie.url)

        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            movie.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + movie.logo)

        movie.title = data['title']
        movie.info = data['info']
        movie.star = data['star']
        movie.tag_id = data['tag_id']
        movie.area = data['area']
        movie.release_time = data['release_time']
        movie.length = data['length']
        db.session.add(movie)
        db.session.commit()
        flash("编辑电影成功", "ok")
        return redirect(url_for("admin.movie_edit", id=movie.id))
    return render_template("admin/movie_edit.html", form=form, movie=movie)


@admin.route("/preview/add", methods=["GET", "POST"])
@admin_login_req
def preview_add():
    form = PreviewForm()
    if form.validate_on_submit():
        data = form.data
        file_logo = secure_filename(form.logo.data.filename)
        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)
        logo = change_filename(file_logo)
        form.logo.data.save(app.config["UP_DIR"] + logo)
        preview = Preview(
            title=data['title'],
            logo=logo
        )
        db.session.add(preview)
        db.session.commit()
        flash("添加预告成功", "ok")
        return redirect(url_for("admin.preview_add"))
    return render_template("admin/preview_add.html", form=form)


# 预告列表
@admin.route("/preview/list/<int:page>/", methods=["GET", "POST"])
@admin_login_req
def preview_list(page=None):
    if page == None:
        page = 1
    page_data = Preview.query.order_by(
        Preview.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/preview_list.html", page_data=page_data)


# 删除预告列表
@admin.route("/preview/del/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def preview_del(id=None):
    preview = Preview.query.get_or_404(int(id))
    db.session.delete(preview)
    db.session.commit()
    flash("预告删除成功", "ok")
    return redirect(url_for("admin.preview_list", page=1))


# 编辑预告列表
@admin.route("/preview/edit/<int:id>/", methods=["GET", "POST"])
@admin_login_req
def preview_edit(id=None):
    form = PreviewForm()
    preview = Preview.query.get_or_404(int(id))
    if request.method == "GET":
        form.title.data = preview.title
    form.logo.validators = []
    if form.validate_on_submit():
        data = form.data
        preview_count = Preview.query.filter_by(title=data['title']).count()
        if preview_count >= 1 and preview.title != data['title']:
            flash("预告名已存在", "err")
            return redirect(url_for("admin.preview_edit", id=preview.id))

        if not os.path.exists(app.config["UP_DIR"]):
            os.makedirs(app.config["UP_DIR"])
            os.chmod(app.config["UP_DIR"], stat.S_IRWXU)

        if form.logo.data != "":
            file_logo = secure_filename(form.logo.data.filename)
            preview.logo = change_filename(file_logo)
            form.logo.data.save(app.config['UP_DIR'] + preview.logo)

        preview.title = data['title']
        db.session.add(preview)
        db.session.commit()
        flash("修改预告成功", "ok")
        return redirect(url_for("admin.preview_edit", id=preview.id))
    return render_template("admin/preview_edit.html", form=form, preview=preview)


# 会员列表
@admin.route("/user/list/<int:page>/", methods=["GET"])
@admin_login_req
def user_list(page=None):
    if page == None:
        page = 1
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)


# 会员详情页面
@admin.route("/user/view/<int:id>/", methods=["GET"])
@admin_login_req
def user_view(id=None):
    user = User.query.get_or_404(int(id))
    return render_template("admin/user_view.html", user=user)


# 删除会员
@admin.route("/user/del/<int:id>/", methods=["GET"])
@admin_login_req
def user_del(id=None):
    user = User.query.get_or_404(int(id))
    db.session.delete(user)
    db.session.commit()
    flash("删除会员成功", "ok")
    page_data = User.query.order_by(
        User.addtime.desc()
    ).paginate(page=1, per_page=10)
    return render_template("admin/user_list.html", page_data=page_data)


# 评论列表
@admin.route("/comment/list/<int:page>/")
@admin_login_req
def comment_list(page=None):
    if page == None:
        page = 1
    page_data = Comment.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Comment.movie_id,
        User.id == Comment.user_id
    ).order_by(
        Comment.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)


# 删除评论
@admin.route("/comment/del/<int:id>/", methods=["GET"])
@admin_login_req
def comment_del(id=None):
    comment = Comment.query.get_or_404(int(id))
    db.session.delete(comment)
    db.session.commit()
    flash("删除评论成功", "ok")
    page_data = Comment.query.order_by(
        Comment.addtime.desc()
    ).paginate(page=1, per_page=10)
    return render_template("admin/comment_list.html", page_data=page_data)

# 收藏列表
@admin.route("/moviecol/list/<int:page>/", methods=["GET","POST"])
@admin_login_req
def moviecol_list(page=None):
    if page ==None:
        page =1
    page_data = Moviecol.query.join(
        Movie
    ).join(
        User
    ).filter(
        Movie.id == Moviecol.movie_id,
        User.id == Moviecol.user_id
    ).order_by(
        Moviecol.addtime.desc()
    ).paginate(page=page, per_page=10)
    return render_template("admin/moviecol_list.html", page_data=page_data)


@admin.route("/oplog/list")
@admin_login_req
def oplog_list():
    return render_template("admin/oplog_list.html")


@admin.route("/adminloginlog/list")
@admin_login_req
def adminloginlog_list():
    return render_template("admin/adminloginlog_list.html")


@admin.route("/userloginlog/list")
@admin_login_req
def userloginlog_list():
    return render_template("admin/userloginlog_list.html")


@admin.route("/auth/add")
@admin_login_req
def auth_add():
    return render_template("admin/auth_add.html")


@admin.route("/auth/list")
@admin_login_req
def auth_list():
    return render_template("admin/auth_list.html")


@admin.route("/role/add")
@admin_login_req
def role_add():
    return render_template("admin/role_add.html")


@admin.route("/role/list")
@admin_login_req
def role_list():
    return render_template("admin/role_list.html")


@admin.route("/admin/add")
@admin_login_req
def admin_add():
    return render_template("admin/admin_add.html")


@admin.route("/admin/list")
@admin_login_req
def admin_list():
    return render_template("admin/admin_list.html")
