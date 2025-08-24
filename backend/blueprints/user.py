from flask import Blueprint, response, body, authenticate
from models.user import User
from models.token import Token
from schema.users import UserSchema, LoginSchema, RegisterSchema
from auth import token_auth

users = Blueprint("users", __name__)


@users.route("/login", methods=["POST"])
@body(LoginSchema)
def login(args):
    username = args.get("username", None)
    password = args.get("password", None)
    user = User.get_user_by_username(username)
    if user is None:
        return {"error": "No user found"}, 404
    print(user.verify_password(password))
    result = user.verify_password(password)
    if not result:
        return {"error": "Incorrect password"}, 403
    return Token(user=user.uid)


@users.route("/get_user", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema)
def get_user(args):
    user = token_auth.current_user()
    if user is None:
        return {"error": "No user is found"}, 404
    return user


@users.route("/register", methods=["POST"])
@body(RegisterSchema)
@response(UserSchema)
def register():
    username = args.get("username", None)
    password = args.get("password", None)
    confirm_password = args.get("confirm_password", None)
    pass


@users.route("/forgot_password", methods=["POST"])
def forgot_password():
    pass


@users.route("/update_user", methods=["PUT"])
def update():
    pass
