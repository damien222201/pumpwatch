"""
PumpWatch
---------
Crowdsourced fuel price tracker for Nigeria. People report what they paid
for petrol (PMS) or diesel (AGO) at a station, and anyone can check recent
reported prices for their state, or see which states are cheapest/priciest.

No official live API publishes station-level pump prices — this is
community-reported by design, same as LightWatch.
"""
import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from models import db, PriceReport
from reference_data import STATES, FUEL_TYPES
from utils import is_valid_email, is_sane_price, is_rate_limited, recent_prices, state_averages, national_average


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    database_url = os.environ.get("DATABASE_URL", "sqlite:///pumpwatch_dev.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        recent = PriceReport.query.order_by(PriceReport.created_at.desc()).limit(20).all()
        return render_template("index.html", states=STATES, fuel_types=FUEL_TYPES, recent=recent)

    @app.route("/report", methods=["POST"])
    def report():
        email = request.form.get("email", "").strip()
        state = request.form.get("state", "").strip()
        station_area = request.form.get("station_area", "").strip()
        fuel_type = request.form.get("fuel_type", "").strip()
        price = request.form.get("price_per_litre", "").strip()
        note = request.form.get("note", "").strip() or None
        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("index"))
        if state not in STATES:
            flash("Please select a valid state.", "error")
            return redirect(url_for("index"))
        if not station_area or len(station_area) > 200:
            flash("Please enter the station name or area.", "error")
            return redirect(url_for("index"))
        if fuel_type not in FUEL_TYPES:
            flash("Please select a valid fuel type.", "error")
            return redirect(url_for("index"))
        if not is_sane_price(price):
            flash("Please enter a realistic price per litre (in Naira).", "error")
            return redirect(url_for("index"))
        if is_rate_limited(email, ip_address):
            flash("You've submitted a few reports recently — please wait a bit before reporting again.", "error")
            return redirect(url_for("index"))

        new_report = PriceReport(
            email=email, state=state, station_area=station_area,
            fuel_type=fuel_type, price_per_litre=float(price),
            note=note, ip_address=ip_address,
        )
        db.session.add(new_report)
        db.session.commit()

        flash("Thanks — your price report has been logged.", "success")
        return redirect(url_for("index"))

    @app.route("/prices")
    def prices():
        state = request.args.get("state", "").strip()
        fuel_type = request.args.get("fuel_type", "PMS").strip()
        if fuel_type not in FUEL_TYPES:
            fuel_type = "PMS"

        results = recent_prices(state, fuel_type) if state in STATES else []
        return render_template(
            "prices.html", states=STATES, fuel_types=FUEL_TYPES,
            state=state, fuel_type=fuel_type, results=results,
        )

    @app.route("/stats")
    def stats():
        fuel_type = request.args.get("fuel_type", "PMS").strip()
        if fuel_type not in FUEL_TYPES:
            fuel_type = "PMS"
        days = request.args.get("days", default=7, type=int)
        if days not in (7, 30):
            days = 7

        averages = state_averages(fuel_type, days=days)
        national = national_average(fuel_type, days=days)
        total_reports = PriceReport.query.filter_by(fuel_type=fuel_type).count()

        return render_template(
            "stats.html", fuel_types=FUEL_TYPES, fuel_type=fuel_type, days=days,
            averages=averages, national=national, total_reports=total_reports,
        )

    @app.route("/api/reports")
    def api_reports():
        since = datetime.utcnow() - timedelta(hours=72)
        reports = PriceReport.query.filter(PriceReport.created_at >= since).order_by(PriceReport.created_at.desc()).all()
        return jsonify([r.to_dict() for r in reports])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
