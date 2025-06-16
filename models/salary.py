import pytz
from models import db
from datetime import datetime, timezone

class Salary(db.Model):
    __tablename__ = 'salary'

    id = db.Column(db.Integer(), primary_key=True)

    type = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float(), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, type, amount):
        super().__init__()
        self.type = type
        self.amount = amount
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
