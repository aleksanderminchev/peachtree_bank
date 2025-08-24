from flask import current_app, request, make_response, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from functools import wraps
from werkzeug.exceptions import Unauthorized, Forbidden

from app import db
from models.user import User
from models.token import Token

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(access_token):
    if current_app.config["DISABLE_AUTH"]:
        user = db.session.get(User, 1)
        return user
    if access_token:
        decoded_data = Token.decode_access_token(access_token)
        access_token_db = Token.find_by_access_token(decoded_data["token"])
        if access_token_db.is_valid():
            return ""
        else:
            if not access_token_db.is_refresh_expired():
                new_token = Token.get_access_jwt(access_token)


@token_auth.error_handler
def token_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description,
    }, error.code
