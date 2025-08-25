from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from apifairy import authenticate, body, response, other_responses

from sqlalchemy.orm import joinedload
from app import db
from models.transactions import Transaction
from schema.transactions import AddTransactionSchema, TransactionSchema
from models.contractors import Contractor  # Assuming this exists
from models.enums import CurrencyEnum, TransactionStatus, MethodEnum
from utils.utils import get_date
import hashlib
import uuid
from datetime import datetime

transactions = Blueprint("transactions", __name__)


@transactions.route("/add_transaction", methods=["POST"])
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

        contractor = Contractor.query.get(contractor_id)
        if not contractor:
            contractor = Contractor(name=contractor_name)

        currency = data.get("currency", CurrencyEnum.USD.value)
        method = data.get("method", MethodEnum.TRANSACTION.value)

        # Generate tracking_id
        unique_string = f"{data['contractor_id']}_{data['amount']}_{get_date().isoformat()}_{uuid.uuid4()}"
        tracking_id = hashlib.sha256(unique_string.encode()).hexdigest()

        # Create new transaction
        transaction = Transaction(
            contractor_id=data["contractor_id"],
            amount=amount,
            currency=currency,
            method=method,
            tracking_id=data.get("tracking_id", tracking_id),
            sent_at=get_date(),
            status=TransactionStatus.SENT.value,
        )

        db.session.add(transaction)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Transaction created successfully",
                    "transaction": {
                        "uid": transaction.uid,
                        "status": transaction.status.value,
                        "amount": transaction.amount,
                        "currency": transaction.currency.value,
                        "method": transaction.method.value,
                        "contractor": (
                            {
                                "uid": transaction.contractor.uid,
                                "name": transaction.contractor.name,
                            }
                            if transaction.contractor
                            else None
                        ),
                        "tracking_id": transaction.tracking_id,
                        "created_at": (
                            transaction.created_at.isoformat()
                            if transaction.created_at
                            else None
                        ),
                        "received_at": (
                            transaction.received_at.isoformat()
                            if transaction.received_at
                            else None
                        ),
                        "sent_at": (
                            transaction.sent_at.isoformat()
                            if transaction.sent_at
                            else None
                        ),
                        "payed_at": (
                            transaction.payed_at.isoformat()
                            if transaction.payed_at
                            else None
                        ),
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@transactions.route("/get_transaction/<int:id>", methods=["GET"])
def get_transaction(id):
    """
    Get a single transaction by ID
    """
    try:
        schema = TransactionSchema()
        print(id)
        transaction = Transaction.get_transaction_by_id(id)
        if transaction:
            return (schema.dump(transaction), 200)
        else:
            return {"error": "No transaction found"}, 404
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@transactions.route("/get_transactions", methods=["GET"])
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


@transactions.route("/update_transaction", methods=["PUT"])  # Fixed typo in route name
def update_transaction():
    """
    Update an existing transaction
    Expected JSON payload:
    {
        "uid": int (required),
        "status": str (optional),
        "sent_at": str (optional) - ISO format datetime,
        "payed_at": str (optional) - ISO format datetime,
        "tracking_id": str (optional),
        "amount": float (optional),
        "currency": str (optional),
        "method": str (optional)
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        if "uid" not in data:
            return jsonify({"error": "Transaction uid is required"}), 400

        transaction = Transaction.query.get(data["uid"])
        if not transaction:
            return jsonify({"error": "Transaction not found"}), 404

        # Update fields if provided
        if "status" in data:
            try:
                status = TransactionStatus(data["status"])
                transaction.status = status.value
            except ValueError:
                return jsonify({"error": f"Invalid status: {data['status']}"}), 400

        if "sent_at" in data:
            if data["sent_at"]:
                try:
                    transaction.sent_at = datetime.fromisoformat(
                        data["sent_at"].replace("Z", "+00:00")
                    )
                except ValueError:
                    return (
                        jsonify({"error": "Invalid sent_at format. Use ISO format."}),
                        400,
                    )
            else:
                transaction.sent_at = None

        if "payed_at" in data:
            if data["payed_at"]:
                try:
                    transaction.payed_at = datetime.fromisoformat(
                        data["payed_at"].replace("Z", "+00:00")
                    )
                except ValueError:
                    return (
                        jsonify({"error": "Invalid payed_at format. Use ISO format."}),
                        400,
                    )
            else:
                transaction.payed_at = None

        if "tracking_id" in data:
            transaction.tracking_id = data["tracking_id"]

        if "amount" in data:
            if data["amount"] <= 0:
                return jsonify({"error": "Amount must be positive"}), 400
            transaction.amount = data["amount"]

        if "currency" in data:
            try:
                currency = CurrencyEnum(data["currency"])
                transaction.currency = currency.value
            except ValueError:
                return jsonify({"error": f"Invalid currency: {data['currency']}"}), 400

        if "method" in data:
            try:
                method = MethodEnum(data["method"])
                transaction.method = method.value
            except ValueError:
                return jsonify({"error": f"Invalid method: {data['method']}"}), 400

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Transaction updated successfully",
                    "transaction": {
                        "uid": transaction.uid,
                        "status": transaction.status,
                        "sent_at": (
                            transaction.sent_at.isoformat()
                            if transaction.sent_at
                            else None
                        ),
                        "payed_at": (
                            transaction.payed_at.isoformat()
                            if transaction.payed_at
                            else None
                        ),
                        "received_at": (
                            transaction.received_at.isoformat()
                            if transaction.received_at
                            else None
                        ),
                        "currency": transaction.currency,
                        "amount": transaction.amount,
                        "method": transaction.method,
                        "tracking_id": transaction.tracking_id,
                        "contractor_id": transaction.contractor_id,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
