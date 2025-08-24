from flask import Blueprint

transactions = Blueprint("users", __name__)


@transactions.route("/add_transaction", methods=["POST"])
def login():
    pass


@transactions.route("/get_transaction", methods=["POST"])
def get_transaction():
    pass


@transactions.route("/get_transactions", methods=["POST"])
def get_transactions():
    pass


@transactions.route("/update_transation", methods=["PUT"])
def update():
    pass
