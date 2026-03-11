"""
Modelos de SQLAlchemy para la aplicación de la Dra. Lina.
"""
from flask_login import UserMixin
from datetime import datetime, timezone
from .extensions import db


class AppointmentStatus:
    PENDING = 'pendiente_confirmacion'
    CONFIRMED = 'confirmada'
    CANCELLED = 'cancelada'
    COMPLETED = 'completada'
    NO_SHOW = 'no_asistio'

    ALL = [PENDING, CONFIRMED, CANCELLED, COMPLETED, NO_SHOW]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    role = db.Column(db.String(20), default='admin')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    document_id = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    appointments = db.relationship('Appointment', backref='patient', lazy=True)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    price = db.Column(db.Float, nullable=False)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default=AppointmentStatus.PENDING)
    confirmation_token = db.Column(db.String(500))
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_appointments')
    service = db.relationship('Service')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=True)
    content = db.Column(db.Text, nullable=False)
    featured_image_url = db.Column(db.String(500))
    seo_keywords = db.Column(db.String(300))
    references = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_published = db.Column(db.Boolean, default=True)


class DoctorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, default='Doctor')
    specialty = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    color = db.Column(db.String(20), default='#3b82f6')
    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))


class WorkSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    doctor = db.relationship('User', backref='work_schedules')

