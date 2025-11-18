import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

"""
setup_db(app)
    binds a flask application and a SQLAlchemy service
"""
def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


# ------------------------------
# Doctor
# ------------------------------
class Doctor(db.Model):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    speciality = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)

    # Relationship with appointments
    appointments = relationship('Appointment', backref='doctor', lazy=True)

    def __init__(self, name, speciality, phone=None, email=None):
        self.name = name
        self.speciality = speciality
        self.phone = phone
        self.email = email

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'speciality': self.speciality,
            'phone': self.phone,
            'email': self.email
        }

# ------------------------------
# Patient
# ------------------------------
class Patient(db.Model):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String)
    address = Column(String)
    medical_history = Column(String)

    # Relationship with appointments
    appointments = relationship('Appointment', backref='patient', lazy=True)

    def __init__(self, name, phone=None, address=None, medical_history=None):
        self.name = name
        self.phone = phone
        self.address = address
        self.medical_history = medical_history

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'medical_history': self.medical_history
        }

# ------------------------------
# Appointment
# ------------------------------
class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    status = Column(String, nullable=False, default='Scheduled')  # e.g., Scheduled, Canceled, Completed, Reschedule
    notes = Column(String)

    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)

    def __init__(self, date, doctor_id, patient_id, status='Scheduled', notes=None):
        self.date = date
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.status = status
        self.notes = notes

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'date': self.date.isoformat(),
            'doctor_id': self.doctor_id,
            'patient_id': self.patient_id,
            'status': self.status,
            'notes': self.notes
        }