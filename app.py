from flask import Flask
from datetime import timedelta
from models import db, login_manager, migrate

from models.user import User
from models.room_t import RoomT
from models.salary import Salary
from models.qr_code import QRCode
from models.product import Product
from models.invoice import Invoice
from models.client_debt import ClientDebt
from models.main_system import MainSystem
from models.consumption import Consumption
from models.invoice_product import InvoiceProduct

app = Flask(__name__)
app.config["SECRET_KEY"] = "342afc9ac2gfd5435ga1372f913"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://akbarov:akbarov@127.0.0.1:5432/gold_house"
app.config["UPLOAD_FOLDER"] = "static/qr_code"
app.config["WTF_CSRF_ENABLED"] = False
app.config["WTF_CSRF_SECRET_KEY"] = "fgkgsd23gkfsdka34gfd4t43t43"

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    from routes.main_route import *
    from routes.auth_route import *
    from routes.user_route import *
    from routes.room_route import *
    from routes.error_route import *
    from routes.worker_route import *
    from routes.salary_route import *
    from routes.product_route import *
    from routes.invoice_route import *
    from routes.consumption_route import *
    from routes.main_system_route import *
    from routes.client_debt_route import *
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(403, permission_denied)
    app.register_error_handler(401, unauthorized)
    app.run(debug=True, port=8080, host='0.0.0.0')
