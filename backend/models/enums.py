import enum

# File containing all Enums used


class CurrencyEnum(enum.Enum):
    """Currency of the transaction"""

    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class TransactionStatus(enum.Enum):
    """
    State of the transaction
    """

    SENT = "sent"
    RECEIVED = "received"
    PAYED = "payed"


class MethodEnum(enum.Enum):
    """
    Method of payment for transaction

    """

    CARD_PAYMENT = "card payment"
    TRANSACTION = "transaction"
    ONLINE_TRANSFER = "online transfer"
