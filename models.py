"""Database model for PumpWatch."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PriceReport(db.Model):
    __tablename__ = "price_reports"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    state = db.Column(db.String(50), nullable=False, index=True)
    station_area = db.Column(db.String(200), nullable=False)
    fuel_type = db.Column(db.String(5), nullable=False, index=True)  # "PMS" or "AGO"
    price_per_litre = db.Column(db.Numeric(8, 2), nullable=False)
    note = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "station_area": self.station_area,
            "fuel_type": self.fuel_type,
            "price_per_litre": float(self.price_per_litre),
            "note": self.note,
            "created_at": self.created_at.isoformat() + "Z",
        }
