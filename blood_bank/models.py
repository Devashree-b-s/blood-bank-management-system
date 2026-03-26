from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))
    city = db.Column(db.String(50))
    last_donation = db.Column(db.String(20))
    registered_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Donor {self.name} - {self.blood_group}>"


class BloodStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blood_group = db.Column(db.String(5), unique=True, nullable=False)
    units = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Stock {self.blood_group}: {self.units} units>"


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_needed = db.Column(db.Integer, nullable=False)
    hospital = db.Column(db.String(100))
    contact = db.Column(db.String(15))
    status = db.Column(db.String(20), default="Pending")
    requested_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Request {self.patient_name} - {self.blood_group}>"
