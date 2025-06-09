from models import db
from datetime import datetime

class Consumption(db.Model):
    __tablename__ = 'consumption'

    id = db.Column(db.Integer(), primary_key=True)

    type = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.String(300), nullable=False)
    amount = db.Column(db.Float(), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now())

    def __init__(self, type, comment, amount):
        super().__init__()
        self.type = type
        self.comment = comment
        self.amount = amount
        self.created_at = datetime.now()
