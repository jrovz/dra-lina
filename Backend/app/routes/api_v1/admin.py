"""
Admin API v1 endpoints: CRUD for posts, doctors, services, appointments.
All endpoints require JWT authentication.
"""
import logging
from datetime import datetime
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from . import api_v1_bp
from app.serializers import (
    post_schema, posts_schema, post_list_schema,
    doctors_schema, doctor_schema, services_schema, service_schema,
    appointments_schema, appointment_schema, dashboard_stats_schema
)

logger = logging.getLogger(__name__)


# --- Dashboard ---

@api_v1_bp.route('/admin/dashboard/stats')
@jwt_required()
def dashboard_stats():
    from app.models import BlogPost, User, Patient, Appointment, AppointmentStatus
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    stats = {
        'appointments_today': Appointment.query.filter(
            Appointment.start_time.between(today_start, today_end)
        ).count(),
        'appointments_pending': Appointment.query.filter_by(
            status=AppointmentStatus.PENDING
        ).count(),
        'posts_published': BlogPost.query.filter_by(is_published=True).count(),
        'posts_draft': BlogPost.query.filter_by(is_published=False).count(),
        'doctors_count': User.query.filter_by(role='doctor').count(),
        'patients_count': Patient.query.count()
    }
    return jsonify({'data': dashboard_stats_schema.dump(stats)})


# --- Posts CRUD ---

@api_v1_bp.route('/admin/posts')
@jwt_required()
def admin_list_posts():
    from app.models import BlogPost
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = BlogPost.query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data': post_list_schema.dump(pagination.items),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@api_v1_bp.route('/admin/posts', methods=['POST'])
@jwt_required()
def admin_create_post():
    from app.extensions import db
    from app.models import BlogPost

    data = request.get_json()
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'title y content requeridos'}), 400

    post = BlogPost(
        title=data['title'],
        slug=data.get('slug'),
        content=data['content'],
        featured_image_url=data.get('featured_image_url', ''),
        seo_keywords=data.get('seo_keywords', ''),
        references=data.get('references', ''),
        category=data.get('category'),
        author_id=int(get_jwt_identity()),
        is_published=data.get('is_published', True)
    )
    db.session.add(post)
    db.session.commit()
    return jsonify({'data': post_schema.dump(post)}), 201


@api_v1_bp.route('/admin/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def admin_update_post(post_id):
    from app.extensions import db
    from app.models import BlogPost

    post = BlogPost.query.get_or_404(post_id)
    data = request.get_json()

    for field in ['title', 'slug', 'content', 'featured_image_url', 'seo_keywords',
                  'references', 'category', 'is_published']:
        if field in data:
            setattr(post, field, data[field])

    db.session.commit()
    return jsonify({'data': post_schema.dump(post)})


@api_v1_bp.route('/admin/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_post(post_id):
    from app.extensions import db
    from app.models import BlogPost

    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post eliminado'}), 200


# --- Doctors CRUD ---

@api_v1_bp.route('/admin/doctors')
@jwt_required()
def admin_list_doctors():
    from app.models import User, DoctorProfile
    doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
    result = []
    for doc in doctors:
        profile = doc.doctor_profile
        result.append({
            'id': doc.id,
            'username': doc.username,
            'name': profile.name if profile else doc.username,
            'specialty': profile.specialty if profile else '',
            'bio': profile.bio if profile else '',
            'color': profile.color if profile else '#3b82f6'
        })
    return jsonify({'data': result})


@api_v1_bp.route('/admin/doctors', methods=['POST'])
@jwt_required()
def admin_create_doctor():
    from app.extensions import db
    from app.models import User, DoctorProfile

    data = request.get_json()
    required = ['name', 'username', 'password', 'specialty']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f"'{field}' requerido"}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'El usuario ya existe'}), 409

    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='doctor'
    )
    db.session.add(user)
    db.session.commit()

    profile = DoctorProfile(
        user_id=user.id,
        name=data['name'],
        specialty=data['specialty'],
        color=data.get('color', '#3b82f6'),
        bio=data.get('bio', '')
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({'data': {
        'id': user.id,
        'username': user.username,
        'name': profile.name,
        'specialty': profile.specialty
    }}), 201


@api_v1_bp.route('/admin/doctors/<int:doctor_id>', methods=['PUT'])
@jwt_required()
def admin_update_doctor(doctor_id):
    from app.extensions import db
    from app.models import User, DoctorProfile

    user = User.query.get_or_404(doctor_id)
    if user.role != 'doctor':
        return jsonify({'error': 'No es un médico'}), 400

    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
    data = request.get_json()

    if data.get('username'):
        user.username = data['username']
    if data.get('password'):
        user.password_hash = generate_password_hash(data['password'])
    if profile:
        for field in ['name', 'specialty', 'bio', 'color']:
            if field in data:
                setattr(profile, field, data[field])

    db.session.commit()
    return jsonify({'data': doctor_schema.dump({
        'id': user.id,
        'username': user.username,
        'name': profile.name if profile else '',
        'specialty': profile.specialty if profile else ''
    })})


@api_v1_bp.route('/admin/doctors/<int:doctor_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_doctor(doctor_id):
    from app.extensions import db
    from app.models import User, DoctorProfile, WorkSchedule, Appointment

    user = User.query.get_or_404(doctor_id)
    if user.role != 'doctor':
        return jsonify({'error': 'No es un médico'}), 400

    Appointment.query.filter_by(doctor_id=doctor_id).update({'doctor_id': None})
    WorkSchedule.query.filter_by(doctor_id=doctor_id).delete()
    profile = DoctorProfile.query.filter_by(user_id=doctor_id).first()
    if profile:
        db.session.delete(profile)
    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'Médico eliminado'})


# --- Services CRUD ---

@api_v1_bp.route('/admin/services')
@jwt_required()
def admin_list_services():
    from app.models import Service
    return jsonify({'data': services_schema.dump(Service.query.all())})


@api_v1_bp.route('/admin/services', methods=['POST'])
@jwt_required()
def admin_create_service():
    from app.extensions import db
    from app.models import Service

    data = request.get_json()
    if not data.get('name') or data.get('price') is None:
        return jsonify({'error': 'name y price requeridos'}), 400

    service = Service(
        name=data['name'],
        duration_minutes=data.get('duration_minutes', 30),
        price=data['price']
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({'data': service_schema.dump(service)}), 201


@api_v1_bp.route('/admin/services/<int:service_id>', methods=['PUT'])
@jwt_required()
def admin_update_service(service_id):
    from app.extensions import db
    from app.models import Service

    service = Service.query.get_or_404(service_id)
    data = request.get_json()

    for field in ['name', 'duration_minutes', 'price']:
        if field in data:
            setattr(service, field, data[field])

    db.session.commit()
    return jsonify({'data': service_schema.dump(service)})


@api_v1_bp.route('/admin/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
def admin_delete_service(service_id):
    from app.extensions import db
    from app.models import Service

    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    return jsonify({'message': 'Servicio eliminado'})


# --- Appointments Management ---

@api_v1_bp.route('/admin/appointments')
@jwt_required()
def admin_list_appointments():
    from app.models import Appointment

    doctor_id = request.args.get('doctor_id', type=int)
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Appointment.query
    if doctor_id:
        query = query.filter_by(doctor_id=doctor_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Appointment.start_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    result = []
    for appt in pagination.items:
        result.append({
            'id': appt.id,
            'patient_name': appt.patient.name if appt.patient else 'Sin paciente',
            'service_name': appt.service.name if appt.service else 'Sin servicio',
            'doctor_name': appt.doctor.username if appt.doctor else 'Sin doctor',
            'start_time': appt.start_time,
            'status': appt.status,
            'created_at': appt.created_at
        })

    return jsonify({
        'data': appointments_schema.dump(result),
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages
        }
    })


@api_v1_bp.route('/admin/appointments/<int:appt_id>', methods=['PUT'])
@jwt_required()
def admin_update_appointment(appt_id):
    from app.extensions import db
    from app.models import Appointment, AppointmentStatus

    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json()

    new_status = data.get('status')
    if new_status and new_status in AppointmentStatus.ALL:
        appt.status = new_status
        db.session.commit()
        return jsonify({'data': {'id': appt.id, 'status': appt.status}})

    return jsonify({'error': f'Estado inválido. Opciones: {AppointmentStatus.ALL}'}), 400
