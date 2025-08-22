from app import db
from models.basemodel  import BaseModel


class Balance(BaseModel):

    __tablename__ = "balances"

    # general
    uid = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), index=True)
    # One Admin to One User relation
    user = db.relationship("User", backref="balance", uselist=False)

    def __init__(self, user_id=None, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
