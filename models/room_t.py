import pytz
from models import db
from datetime import datetime, timezone

class RoomT(db.Model):
    __tablename__ = 'room_t'

    id = db.Column(db.Integer(), primary_key=True)

    lom = db.Column(db.Float(), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    main_system_id = db.Column(db.Integer(), db.ForeignKey('main_system.id'), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(timezone.utc))

    def __init__(self, lom, main_system_id, comment=None):
        super().__init__()
        self.lom = lom
        self.comment = comment
        self.main_system_id = main_system_id
        time = datetime.now(timezone.utc)
        time = time.astimezone(pytz.timezone('Asia/Tashkent'))
        self.created_at = time
