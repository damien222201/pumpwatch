"""Shared helpers: email validation, rate limiting, and price rollups."""
import re
from datetime import datetime, timedelta
from models import db, PriceReport

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

RATE_LIMIT_WINDOW_MINUTES = 60
RATE_LIMIT_MAX_REPORTS = 5

# Fuel prices move slower than outage status — a report is "fresh" for longer.
PRICE_STALE_HOURS = 72

MIN_SANE_PRICE = 50      # NGN/litre — reject obvious typos below this
MAX_SANE_PRICE = 5000    # NGN/litre — reject obvious typos above this


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def is_sane_price(price):
    try:
        return MIN_SANE_PRICE <= float(price) <= MAX_SANE_PRICE
    except (TypeError, ValueError):
        return False


def is_rate_limited(email, ip_address):
    window_start = datetime.utcnow() - timedelta(minutes=RATE_LIMIT_WINDOW_MINUTES)
    count = PriceReport.query.filter(
        PriceReport.created_at >= window_start,
        db.or_(PriceReport.email == email, PriceReport.ip_address == ip_address),
    ).count()
    return count >= RATE_LIMIT_MAX_REPORTS


def recent_prices(state, fuel_type, limit=20):
    """Most recent reports for a state + fuel type, cheapest first, with staleness flag."""
    since = datetime.utcnow() - timedelta(hours=PRICE_STALE_HOURS)
    reports = (
        PriceReport.query.filter_by(state=state, fuel_type=fuel_type)
        .filter(PriceReport.created_at >= since)
        .order_by(PriceReport.price_per_litre.asc())
        .limit(limit)
        .all()
    )
    stale_cutoff = datetime.utcnow() - timedelta(hours=24)
    results = []
    for r in reports:
        results.append({
            "report": r,
            "is_stale": r.created_at < stale_cutoff,
        })
    return results


def state_averages(fuel_type, days=7):
    """Average reported price per state, for ranking cheapest/priciest."""
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.session.query(
            PriceReport.state,
            db.func.avg(PriceReport.price_per_litre).label("avg_price"),
            db.func.count(PriceReport.id).label("report_count"),
        )
        .filter(PriceReport.fuel_type == fuel_type, PriceReport.created_at >= since)
        .group_by(PriceReport.state)
        .order_by(db.text("avg_price ASC"))
        .all()
    )
    return rows


def national_average(fuel_type, days=7):
    since = datetime.utcnow() - timedelta(days=days)
    avg = (
        db.session.query(db.func.avg(PriceReport.price_per_litre))
        .filter(PriceReport.fuel_type == fuel_type, PriceReport.created_at >= since)
        .scalar()
    )
    return float(avg) if avg is not None else None
