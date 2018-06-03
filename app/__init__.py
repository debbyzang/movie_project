# coding:utf-8

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://bubi:bubi@192.168.5.95/bubi_test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "True"
db = SQLAlchemy(app)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404
