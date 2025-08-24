from flask import Blueprint
from models.transactions import Transaction
from models.user import User
from models.balance import Balance
from models.contractors import Contractor
from models.token import Token
from faker import Faker
from app import db
import random
import string

commands = Blueprint("commands", __name__)
faker = Faker()


@commands.cli.command()
def fill_db():
    faker = Faker("en_UK")
    db.session.configure()  # This might help with the registry issue
    try:
        # generate 10 users with passwords set to admin
        for _ in range(10):
            base_email = faker.email()
            print(base_email)
            username = faker.simple_profile()["username"]
            print(username)
            user = User(
                email=base_email, username=username, password="admin", is_verified=True
            )
            print(user)
            user.tokens = []
            db.session.add(user)
        # generate 500 contractors and random number of transactions per contractor
        for _ in range(500):
            contractor = Contractor(name=f"{faker.company()} {faker.company_suffix()}")
            db.session.add(contractor)
            db.session.flush()
            for _ in range(2):
                method = "card payment"
                amount = round(random.uniform(-2000, 0), 2)
                # Generate random tracking ID
                tracking_id = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=10)
                )
                transaction = Transaction(
                    contractor_id=contractor.uid,
                    currency="USD",
                    tracking_id=tracking_id,
                    method=method,
                    amount=amount,
                    status="sent",
                )
                db.session.add(transaction)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    return ""
