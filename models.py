from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import itsdangerous

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin') # Para la Dra. Lina

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Ej: Consulta General
    duration_minutes = db.Column(db.Integer, default=30)
    price = db.Column(db.Float, nullable=False)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pendiente_confirmacion') # pendiente_confirmacion, confirmada, completada
    confirmation_token = db.Column(db.String(500))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')
    service = db.relationship('Service')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    featured_image_url = db.Column(db.String(500))
    seo_keywords = db.Column(db.String(300))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)

class DoctorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Doctor') # Display name
    specialty = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    color = db.Column(db.String(20), default='#3b82f6') # Hex color for calendar
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))

class WorkSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    doctor = db.relationship('User', backref='work_schedules')

