from flask import Blueprint, request, jsonify
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from app import db
from models.transactions import Transaction
from models.contractors import Contractor  # Assuming this exists
from models.enums import CurrencyEnum, TransactionStatus, MethodEnum
from utils.utils import get_date
import hashlib
import uuid
from datetime import datetime

transactions = Blueprint("transactions", __name__)


@transactions.route("/add_transaction", methods=["POST"])
def add_transaction():
    """
    Add a new transaction
    Expected JSON payload:
    {
        "contractor_id": int,
        "amount": float,
        "currency": str (optional, defaults to USD),
        "method": str (optional, defaults to TRANSACTION),
        "tracking_id": str (optional)
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        required_fields = ["contractor_id", "amount"]
        for field in required_fields:
            if field not in data or data[field] is None:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate contractor exists
        contractor = Contractor.query.get(data["contractor_id"])
        if not contractor:
            return jsonify({"error": "Contractor not found"}), 404

        # Validate amount is positive
        if data["amount"] <= 0:
            return jsonify({"error": "Amount must be positive"}), 400

        # Validate currency if provided
        currency = data.get("currency", CurrencyEnum.USD.value)
        try:
            CurrencyEnum(currency)
        except ValueError:
            return jsonify({"error": f"Invalid currency: {currency}"}), 400

        # Validate method if provided
        method = data.get("method", MethodEnum.TRANSACTION.value)
        try:
            MethodEnum(method)
        except ValueError:
            return jsonify({"error": f"Invalid method: {method}"}), 400

        # Generate hashed_id
        unique_string = f"{data['contractor_id']}_{data['amount']}_{datetime.utcnow().isoformat()}_{uuid.uuid4()}"
        hashed_id = hashlib.sha256(unique_string.encode()).hexdigest()

        # Create new transaction
        transaction = Transaction(
            hashed_id=hashed_id,
            contractor_id=data["contractor_id"],
            amount=data["amount"],
            currency=currency,
            method=method,
            tracking_id=data.get("tracking_id"),
            received_at=datetime.utcnow(),
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
                        "hashed_id": transaction.hashed_id,
                        "status": transaction.status,
                        "amount": transaction.amount,
                        "currency": transaction.currency,
                        "method": transaction.method,
                        "contractor_id": transaction.contractor_id,
                        "tracking_id": transaction.tracking_id,
                        "received_at": (
                            transaction.received_at.isoformat()
                            if transaction.received_at
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
        transaction = Transaction.get_transaction_by_id(id)
        if transaction:
            return (
                jsonify(
                    {
                        "transaction": {
                            "uid": transaction.uid,
                            "hashed_id": transaction.hashed_id,
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
                            "contractor": (
                                {
                                    "uid": transaction.contractor.uid,
                                    "name": transaction.contractor.name,
                                }
                                if transaction.contractor
                                else None
                            ),
                        }
                    }
                ),
                200,
            )
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
            sort_column = Transaction.received_at
        elif sort_by == "contractor":
            query = query.join(Contractor)
            sort_column = Contractor.name
        elif sort_by == "amount":
            sort_column = Transaction.amount
        else:
            return (
                jsonify({"error": "sort_by must be 'date', 'contractor', or 'amount'"}),
                400,
            )

        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Execute paginated query
        paginated_result = query.paginate(page=page, per_page=per_page, error_out=False)
        print(paginated_result)

        transactions_data = []
        for transaction in paginated_result.items:
            print(transaction)
            transactions_data.append(
                {
                    "uid": transaction.uid,
                    "hashed_id": transaction.hashed_id,
                    "status": transaction.status,
                    "sent_at": (
                        transaction.sent_at.isoformat() if transaction.sent_at else None
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
                    "contractor": (
                        {
                            "uid": transaction.contractor.uid,
                            "name": transaction.contractor.name,
                        }
                        if transaction.contractor
                        else None
                    ),
                }
            )

        return (
            jsonify(
                {
                    "transactions": transactions_data,
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
                        "hashed_id": transaction.hashed_id,
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
