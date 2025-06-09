from app import app
from flask import render_template, flash

@app.errorhandler(404)
def page_not_found(e):
    flash("Sahifa topilmadi", "danger")
    return render_template('error/404.html'), 404

@app.errorhandler(403)
def permission_denied(e):
    flash("Ruxsat yetarli emas", "danger")
    return render_template('error/403.html'), 403

@app.errorhandler(401)
def unauthorized(e):
    flash("Tizimga kirilmagan", "danger")
    return render_template('error/401.html'), 401
