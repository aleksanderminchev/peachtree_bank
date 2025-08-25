from flask import Blueprint, request, jsonify
from apifairy import authenticate, body
from auth import token_auth
from sqlalchemy.orm import joinedload
from app import db
from models.transactions import Transaction
from schema.transactions import (
    AddTransactionSchema,
    TransactionSchema,
    UpdateTransactionSchema,
)
from models.contractors import Contractor 
from models.enums import CurrencyEnum, TransactionStatus, MethodEnum
from utils.utils import get_date
import hashlib
import uuid

transactions = Blueprint("transactions", __name__)

transaction_schema = TransactionSchema()


@transactions.route("/add_transaction", methods=["POST"])
@authenticate(token_auth)
@body(AddTransactionSchema)
def add_transaction(data):
    """
    Add a new transaction
    Expected JSON payload:
    {
        "contractor_name": str,
        "contractor_id": int,
        "amount": float,
        "currency": str (optional, defaults to USD),
        "method": str (optional, defaults to TRANSACTION),
        "tracking_id": str (optional)
    }
    """
    try:
        contractor_id = data.get("contractor_id")
        contractor_name = data.get("contractor_name")
        amount = data.get("amount")
        if contractor_id:
            print("brebre")
            contractor = Contractor.query.get(contractor_id)
        else:
            contractor = Contractor.find_by_name(contractor_name)
            print(contractor)
        if not contractor:
            contractor = Contractor(name=contractor_name)
            db.session.add(contractor)
            db.session.commit()
        currency = data.get("currency", CurrencyEnum.USD.value)
        method = data.get("method", MethodEnum.TRANSACTION.value)

        # Generate tracking_id
        unique_string = (
            f"{contractor.uid}_{amount}_{get_date().isoformat()}_{uuid.uuid4()}"
        )
        tracking_id = hashlib.sha256(unique_string.encode()).hexdigest()
        print("berb")
        # Create new transaction
        transaction = Transaction(
            contractor_id=contractor.uid,
            amount=-amount,
            currency=currency,
            method=method,
            tracking_id=data.get("tracking_id", tracking_id),
            sent_at=get_date(),
            status=TransactionStatus.SENT.value,
        )

        db.session.add(transaction)
        db.session.commit()

        return (
            transaction_schema.dump(transaction),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@transactions.route("/get_transaction/<int:id>", methods=["GET"])
@authenticate(token_auth)
def get_transaction(id):
    """
    Get a single transaction by ID
    """
    try:

        transaction = Transaction.get_transaction_by_id(id)
        if transaction:
            return (transaction_schema.dump(transaction), 200)
        else:
            return {"error": "No transaction found"}, 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@transactions.route("/get_transactions", methods=["GET"])
# @authenticate(token_auth)
def get_transactions():
    """
    Get transactions with search and sort functionality
    Query parameters:
    - search (str, optional): search by contractor name
    - sort_by (str, optional): "date", "contractor", "amount" (default: "date")
    - sort_order (str, optional): "asc" or "desc" (default: "desc")
    - page (int, optional): page number for pagination (default: 1)
    - per_page (int, optional): items per page (default: 20)
    - status (str, optional): filter by transaction status
    - contractor_id (int, optional): filter by specific contractor
    """
    try:
        schema = TransactionSchema(many=True)
        # Get query parameters
        search = request.args.get("search")
        sort_by = request.args.get("sort_by", "date")
        sort_order = request.args.get("sort_order", "desc").lower()
        status = request.args.get("status")
        contractor_id = request.args.get("contractor_id")
        try:
            page = int(request.args.get("page", 1))
            per_page = min(int(request.args.get("per_page", 20)), 100)
        except (ValueError, TypeError):
            return jsonify({"error": "page and per_page must be valid integers"}), 400

        query = Transaction.query.options(joinedload(Transaction.contractor))

        # Search by contractor name
        if search:
            search_term = f"%{search}%"
            query = query.join(Contractor).filter(Contractor.name.ilike(search_term))

        # Filter by contractor_id
        if contractor_id:
            try:
                contractor_id = int(contractor_id)
                query = query.filter(Transaction.contractor_id == contractor_id)
            except (ValueError, TypeError):
                return jsonify({"error": "contractor_id must be a valid integer"}), 400

        # Filter by status
        if status:
            try:
                status_enum = TransactionStatus(status)
                query = query.filter(Transaction.status == status_enum.value)
            except ValueError:
                return jsonify({"error": f"Invalid status: {status}"}), 400

        if sort_by == "date":
            sort_column = Transaction.created_at
        elif sort_by == "contractor":
            if not search:
                query = query.join(Contractor)
            sort_column = Contractor.name
        elif sort_by == "amount":
            sort_column = Transaction.amount
        else:
            sort_column = Transaction.amount

        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            print("assc")
            query = query.order_by(sort_column.asc())

        # Execute paginated query
        paginated_result = query.paginate(page=page, per_page=per_page, error_out=False)

        return (
            jsonify(
                {
                    "transactions": schema.dump(paginated_result.items),
                    "pagination": {
                        "page": paginated_result.page,
                        "per_page": paginated_result.per_page,
                        "total": paginated_result.total,
                        "pages": paginated_result.pages,
                        "has_prev": paginated_result.has_prev,
                        "has_next": paginated_result.has_next,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@transactions.route("/update_transaction", methods=["PUT"])
@authenticate(token_auth)
@body(UpdateTransactionSchema)
def update_transaction(data):
    """
    Update an existing transaction
    Expected JSON payload:
    {
        "uid": int (required),
        "status": str (optional),

    }
    """
    try:
        transaction_id = data.get("transaction_id")
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        transaction.update(**data)
        db.session.commit()

        return (
            transaction_schema.dump(transaction),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
