"""
Rutas públicas: Index, Blog, Reservas.
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from datetime import datetime

public_bp = Blueprint('public', __name__)


@public_bp.route('/')
def index():
    from app.models import User, DoctorProfile
    doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
    return render_template('public/index.html', doctors=doctors)


@public_bp.route('/blog')
def blog():
    from app.models import BlogPost
    all_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
    featured_post = all_posts[0] if all_posts else None
    recent_posts = all_posts[1:] if len(all_posts) > 1 else []
    return render_template('public/blog.html', featured_post=featured_post, recent_posts=recent_posts)


@public_bp.route('/blog/<int:post_id>')
def post_detail(post_id):
    from app.models import BlogPost
    post = BlogPost.query.get_or_404(post_id)
    return render_template('public/post_detail.html', post=post)


@public_bp.route('/reservar', methods=['GET', 'POST'])
def reservar():
    from app.extensions import db
    from app.models import Patient, Appointment, Service, DoctorProfile, User
    from app.services.booking import generate_confirmation_token

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        service_id = request.form.get('service_id')
        doctor_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')

        full_date_str = f"{date_str}T{time_str}"
        start_time = datetime.strptime(full_date_str, '%Y-%m-%dT%H:%M')

        patient = Patient.query.filter_by(email=email).first()
        if not patient:
            patient = Patient(name=name, email=email)
            db.session.add(patient)

        token = generate_confirmation_token(email)
        appt = Appointment(
            patient=patient,
            service_id=service_id,
            doctor_id=doctor_id,
            start_time=start_time,
            confirmation_token=token
        )
        db.session.add(appt)
        db.session.commit()

        print(f"Token generado para {email}: {token}")
        return render_template('public/success_booking.html', email=email)

    services = Service.query.all()
    doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
    return render_template('public/reservar.html', services=services, doctors=doctors)


@public_bp.route('/confirmar/<token>')
def confirmar_cita(token):
    from app.extensions import db
    from app.models import Appointment
    from app.services.booking import confirm_token

    email = confirm_token(token)
    if email:
        appt = Appointment.query.filter_by(confirmation_token=token).first()
        if appt:
            appt.status = 'confirmada'
            db.session.commit()
            return "Cita confirmada con éxito. ¡Te esperamos!"

    return "Token inválido o expirado.", 400
