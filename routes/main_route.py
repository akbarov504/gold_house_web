import qrcode
import calendar
import models.user
import models.room_t
from app import app
import models.salary
from os import remove
from models import db
import models.qr_code
import models.invoice
import models.product
from os.path import join
import models.client_debt
import models.consumption
import models.main_system
from datetime import date
from datetime import datetime
from flask_login import login_required
from forms.qr_code_form import CreateQRCodeForm
from flask import render_template, request, flash, redirect, url_for

EXCHANGE_DATA = {
    "UZS": "13000",
    "GOLD": "100"
}

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
@app.route("/index", methods=["GET"])
@login_required
def home_page():
    labels = ['Yanvar', 'Febral', 'Mart', 'Aprel', 'May', 'Iyun', 'Iyul', 'Avgust', 'Sentyabr', 'Oktyabr', 'Noyabr', 'Dekabr']
    data = []
    for i in range(1, 13):
        year = date.today().year
        last_day = calendar.monthrange(year, i)

        start_date = date(year, i, 1)
        end_date = date(year, i, last_day[-1])
        
        invoice_list = models.invoice.Invoice.query.filter(models.invoice.Invoice.created_at.between(start_date, end_date)).all()
        data.append(len(invoice_list))

    product_list = models.product.Product.query.filter_by(status="NEW").all()
    product_total_price = 0
    for product in product_list:
        product_total_price += product.price

    main_system_list = models.main_system.MainSystem.query.order_by(models.main_system.MainSystem.created_at.desc()).all()
    room_list = models.room_t.RoomT.query.all()

    consumption_total_amount = 0
    consumption_list = models.consumption.Consumption.query.all()
    for consumption in consumption_list:
        consumption_total_amount += consumption.amount
    
    gold = EXCHANGE_DATA["GOLD"]
    uzs = EXCHANGE_DATA["UZS"]
    consumption_total_amount = ((consumption_total_amount / float(uzs)) / float(gold))
    consumption_total_amount = round(consumption_total_amount, 2)

    product_new_total_amount = 0
    product_new_list = models.product.Product.query.filter_by(status="NEW").all()
    for product_new in product_new_list:
        product_new_total_amount += product_new.price
    product_new_total_amount = round(product_new_total_amount, 2)

    product_invoice_total_amount = 0
    product_invoice_list = models.product.Product.query.filter_by(status="INVOICE").all()
    for product_invoice in product_invoice_list:
        product_invoice_total_amount += product_invoice.price
    product_invoice_total_amount = round(product_invoice_total_amount, 2)

    client_total_debt = 0
    client_list = models.user.User.query.filter_by(role="CLIENT").all()
    for client in client_list:
        client_debt_list = models.client_debt.ClientDebt.query.filter_by(user_id=client.id).all()
        for client_debt in client_debt_list:
            client_total_debt += client_debt.lom
    client_total_debt = round(client_total_debt, 2)

    total = consumption_total_amount + product_new_total_amount + product_invoice_total_amount + client_total_debt
    qr_code_list = models.qr_code.QRCode.query.order_by(models.qr_code.QRCode.created_at.desc()).all()
    return render_template("index.html", labels=labels, data=data, exchange_data=EXCHANGE_DATA, product_count=len(product_list), product_total_price=product_total_price, main_system_list=main_system_list, consumption_total_amount=consumption_total_amount, product_new_total_amount=product_new_total_amount, product_invoice_total_amount=product_invoice_total_amount, client_total_debt=client_total_debt, room_list=room_list, total=total, qr_code_list=qr_code_list)

@app.route("/exchange/dollor", methods=['POST'])
@login_required
def exchange_dollor():
    if request.method == "POST":
        new_dollor = request.form["dollor"]
        global EXCHANGE_DATA
        EXCHANGE_DATA["UZS"] = new_dollor

        flash("Dollar kursi muvaffaqiyatli yangilandi", "success")
        return redirect(url_for("home_page"))
    else:
       return redirect(url_for("home_page"))

@app.route("/exchange/gold", methods=['POST'])
@login_required
def exchange_gold():
    if request.method == "POST":
        new_gold = request.form["gold"]
        global EXCHANGE_DATA
        EXCHANGE_DATA["GOLD"] = new_gold
        
        flash("Oltin narxi muvaffaqiyatli yangilandi", "success")
        return redirect(url_for("home_page"))
    else:
       return redirect(url_for("home_page")) 

@app.route("/add/qr_code", methods=["GET", "POST"])
@login_required
def add_qr_code():
    form = CreateQRCodeForm()
    title_list = ["КАЛЬЦО", "СЕРЬГИ", "КУЛОН"]
    type_list = [s.type for s in models.salary.Salary.query.all()]
    form.title.choices = title_list
    form.type.choices = type_list
    if form.validate_on_submit():
        title = form.title.data
        gramm = form.gramm.data
        proba = form.proba.data
        type = form.type.data
        number = form.number.data
        size = form.size.data

        new_qr_code = models.qr_code.QRCode(title, gramm, proba, type, number, size)
        db.session.add(new_qr_code)
        db.session.commit()

        qr_data = new_qr_code.id
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(qr_data)
        qr.make()
        img = qr.make_image(fill_color="black", back_color="white")

        filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path = join(app.config['UPLOAD_FOLDER'], filename)
        img.save(file_path)

        new_qr_code.qr_code = filename
        db.session.commit()

        flash("Qr code successfully created", "success")
        return redirect(url_for("home_page"))
    else:
        return render_template("qr_code/qr_code_create.html", form=form)

@app.route("/qr_code/delete/<qr_code_id>", methods=["GET", "POST"])
@login_required
def qr_code_delete_page(qr_code_id):
    if request.method == "POST":
        deleted_qr_code = models.qr_code.QRCode.query.filter_by(id=qr_code_id).first()
        db.session.delete(deleted_qr_code)
        db.session.commit()

        remove(join(app.config['UPLOAD_FOLDER'], deleted_qr_code.qr_code))
        flash("QR Code successfully deleted", "warning")
        return redirect(url_for("home_page"))
    else:
        return render_template("qr_code/qr_code_delete.html", qr_code_id=qr_code_id)

@app.route("/qr_code/print/<qr_code_id>", methods=["GET"])
@login_required
def qr_code_print_page(qr_code_id):
    qr_code_print = models.qr_code.QRCode.query.filter_by(id=qr_code_id).first()
    if qr_code_print:
        return render_template("qr_code/qr_code_print.html", qr_code=qr_code_print)
    else:
        flash("QR Code not found", "danger")
        return redirect(url_for("home_page"))
