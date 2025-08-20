import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


def as_bool(value):
    if value:
        return value.lower() in ["true", "yes", "on", "1"]
    return False


sqlalchemy_pool_size = os.environ.get("SQLALCHEMY_POOL_SIZE") or 2
sqlalchemy_max_overflow = os.environ.get("SQLALCHEMY_MAX_OVERFLOW") or 3


class Config(object):
    """
    Config File with all env configurations present_
    """


class DevelopmentConfig(Config):
    ENV_NAME = "development"
    DEBUG = True
    # DEVELOPMENT DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI_DEV")
    SQLALCHEMY_BINDS = {
        "meta": "sqlite:////path/to/meta.db",
    }

    SQLALCHEMY_ECHO = as_bool(os.environ.get("SQLALCHEMY_ECHO") or "false")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(sqlalchemy_pool_size),
        "max_overflow": int(sqlalchemy_max_overflow),
        "pool_recycle": 60,  # Recycle connections every 30 minutes
        "pool_pre_ping": True,  # Enable pre-ping to check connection validity
        "pool_timeout": 30,  # Timeout for acquiring a connection from the pool
    }


class ProductionConfig(Config):
    # DEVELOPMENT DATABASE
    ENV_NAME = "production"
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI_PRODUCTION")
    SQLALCHEMY_ECHO = as_bool(os.environ.get("SQLALCHEMY_ECHO") or "false")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(sqlalchemy_pool_size),
        "max_overflow": int(sqlalchemy_max_overflow),
        "pool_recycle": 60,  # Recycle connections every 30 minutes
        "pool_pre_ping": True,  # Enable pre-ping to check connection validity
        "pool_timeout": 30,  # Timeout for acquiring a connection from the pool
    }


class TestingConfig(Config):
    ENV_NAME = "testing"
    # DEVELOPMENT DATABASE
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI_TEST")
    SQLALCHEMY_ECHO = as_bool(os.environ.get("SQLALCHEMY_ECHO") or "false")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": int(sqlalchemy_pool_size),
        "max_overflow": int(sqlalchemy_max_overflow),
        "pool_recycle": 60,  # Recycle connections every 30 minutes
        "pool_pre_ping": True,  # Enable pre-ping to check connection validity
        "pool_timeout": 30,  # Timeout for acquiring a connection from the pool
    }


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
