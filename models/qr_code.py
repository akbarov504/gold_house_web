import pytz
from models import db
from datetime import datetime, timezone

class QRCode(db.Model):
    __tablename__ = 'qr_code'

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    gramm = db.Column(db.Float(), nullable=False)
    proba = db.Column(db.Float(), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer(), nullable=False)
    size = db.Column(db.Float(), nullable=True, default=0)
    qr_code = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, title, gramm, proba, type, number, size):
        super().__init__()
        self.title = title
        self.gramm = gramm
        self.proba = proba
        self.type = type
        self.number = number
        self.size = size
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
