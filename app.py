import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db_ivan.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# endpoint to create new user
@app.route("/user-registration", methods=["POST"])
def add_user():
    print(request.json)
    username = request.json['username']
    password = request.json['password']
    print(username, password)
    new_user = User(username, password)

    db.session.add(new_user)
    db.session.commit()

    return {'result': True}


# ручка для отображения всех пользователей
@app.route("/login", methods=["POST"])
def login_user():
    user = User.query.filter(User.username == request.json['username']).first()
    if user and user.check_password(request.json['password']):
        return {'result': True}
    return {'result': 'Invalid username/password'}


# ручка для отображения всех пользователей
@app.route("/user", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    print(result)
    return jsonify(result)


# ручка, для отображения пользователя по id
@app.route("/user/<id>", methods=["GET"])
def user_detail(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)


# ручка, для обновления данных пользователя по id
@app.route("/user/<id>", methods=["PUT"])
def user_update(id):
    user = User.query.get(id)
    username = request.json['username']
    password = request.json['password']

    user.password = generate_password_hash(password)
    user.username = username

    db.session.commit()
    return user_schema.jsonify(user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', debug=True)
