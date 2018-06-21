# coding:utf-8

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.debug = True

from app.home import home as home_blueprint
from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
app.register_blueprint(admin_blueprint, url_prefix="/admin")
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://bubi:bubi@192.168.5.95/bubi_test"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = "True"
app.config['SECRET_KEY'] = '33856dc54007478197fc3acd92f4441b'
app.config['UP_DIR'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), "static/uploads/")
db = SQLAlchemy(app)

@app.errorhandler(404)
def page_not_found(error):
    return render_template("home/404.html"), 404
