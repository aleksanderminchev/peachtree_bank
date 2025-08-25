from flask import current_app, request, make_response, jsonify, g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from functools import wraps
from werkzeug.exceptions import Unauthorized, Forbidden

from app import db
import app
from models.user import User
from models.token import Token
from utils.utils import get_date

token_auth = HTTPTokenAuth()


@token_auth.verify_token
def verify_token(access_token):
    # Disable auth for testing user client side
    if current_app.config.get("DISABLE_AUTH", True):
        user = db.session.get(User, 1)
        return user
    if access_token:
        user = Token.verify_access_token(access_token)
        return user


@token_auth.error_handler
def token_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description,
    }, error.code
