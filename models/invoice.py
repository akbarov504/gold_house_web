import pytz
from models import db
from datetime import datetime, timezone

class Invoice(db.Model):
    __tablename__ = 'invoice'

    id = db.Column(db.Integer, primary_key=True)

    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(10), nullable=False)
    total_price = db.Column(db.Float(), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, invoice_number, user_id, status, total_price):
        super().__init__()
        self.invoice_number = invoice_number
        self.user_id = user_id
        self.status = status
        self.total_price = total_price
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
