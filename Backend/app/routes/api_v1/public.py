"""
Public API v1 endpoints: blog, doctors, services, slots, appointments.
No authentication required.
"""
from flask import request, jsonify
from datetime import datetime
from . import api_v1_bp
from app.serializers import (
    post_list_schema, post_schema, doctors_schema, doctor_schema,
    services_schema, appointment_schema
)


@api_v1_bp.route('/blog/posts')
def list_posts():
    from app.models import BlogPost
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    category = request.args.get('category')

    query = BlogPost.query.filter_by(is_published=True)
    if category:
        query = query.filter_by(category=category)

    pagination = query.order_by(BlogPost.created_at.desc()).paginate(
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


@api_v1_bp.route('/blog/posts/<slug>')
def get_post_by_slug(slug):
    from app.models import BlogPost
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first()
    if not post:
        post = BlogPost.query.filter_by(id=slug, is_published=True).first() if slug.isdigit() else None
    if not post:
        return jsonify({'error': 'Post no encontrado'}), 404
    return jsonify({'data': post_schema.dump(post)})


@api_v1_bp.route('/doctors')
def list_doctors():
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


@api_v1_bp.route('/doctors/<int:doctor_id>/slots')
def get_doctor_slots(doctor_id):
    from app.models import Service
    from app.services.booking import get_available_slots

    date_str = request.args.get('date')
    service_id = request.args.get('service_id', type=int)

    if not date_str or not service_id:
        return jsonify({'error': 'date y service_id requeridos'}), 400

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}), 400

    service = Service.query.get(service_id)
    if not service:
        return jsonify({'error': 'Servicio no encontrado'}), 404

    slots = get_available_slots(doctor_id, date_obj, service.duration_minutes)
    return jsonify({'data': slots})


@api_v1_bp.route('/services')
def list_services():
    from app.models import Service
    all_services = Service.query.all()
    return jsonify({'data': services_schema.dump(all_services)})


@api_v1_bp.route('/appointments', methods=['POST'])
def create_appointment():
    from app.extensions import db
    from app.models import Patient, Appointment, Service, User, DoctorProfile
    from app.services.booking import generate_confirmation_token, check_availability

    data = request.get_json()
    required = ['name', 'document_id', 'phone', 'age', 'service_id', 'doctor_id', 'date', 'time']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f"Campo '{field}' requerido"}), 400

    try:
        start_time = datetime.strptime(f"{data['date']}T{data['time']}", '%Y-%m-%dT%H:%M')
    except ValueError:
        return jsonify({'error': 'Formato de fecha/hora inválido'}), 400

    service = Service.query.get(data['service_id'])
    if not service:
        return jsonify({'error': 'Servicio no encontrado'}), 404

    duration = service.duration_minutes
    if not check_availability(data['service_id'], start_time, duration):
        return jsonify({'error': 'El horario seleccionado ya no está disponible'}), 409

    patient = Patient.query.filter_by(document_id=data['document_id']).first()
    if not patient:
        patient = Patient(
            name=data['name'],
            document_id=data['document_id'],
            email=data.get('email'),
            phone=data['phone'],
            age=data['age']
        )
        db.session.add(patient)
    else:
        patient.name = data['name']
        patient.email = data.get('email')
        patient.phone = data['phone']
        patient.age = data['age']

    token_seed = data.get('email') or data['document_id']
    token = generate_confirmation_token(token_seed)

    appt = Appointment(
        patient=patient,
        service_id=data['service_id'],
        doctor_id=data['doctor_id'],
        start_time=start_time,
        confirmation_token=token
    )
    db.session.add(appt)
    db.session.commit()

    return jsonify({
        'data': appointment_schema.dump({
            'id': appt.id,
            'patient_name': patient.name,
            'service_name': service.name,
            'start_time': appt.start_time,
            'status': appt.status,
            'created_at': appt.created_at
        }),
        'confirmation_token': token
    }), 201
