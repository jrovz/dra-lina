"""
Rutas del panel de administración.
"""
import os
import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    from app.models import User
    from app.forms import LoginForm

    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.admin_dashboard'))
        else:
            flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@login_required
def admin_dashboard():
    gemini_key = os.getenv('GEMINI_API_KEY', '')
    openai_key = os.getenv('OPENAI_API_KEY', '')

    gemini_configured = bool(gemini_key and not gemini_key.startswith('AIza-tu'))
    openai_configured = bool(openai_key and not openai_key.startswith('sk-tu'))

    gemini_masked = (gemini_key[:8] + '...' + gemini_key[-4:]) if len(gemini_key) > 12 else ''
    openai_masked = (openai_key[:7] + '...' + openai_key[-4:]) if len(openai_key) > 11 else ''

    return render_template(
        'admin/dashboard.html',
        gemini_configured=gemini_configured,
        openai_configured=openai_configured,
        gemini_key_masked=gemini_masked,
        openai_key_masked=openai_masked
    )


@admin_bp.route('/api/settings', methods=['POST'])
@login_required
def api_save_settings():
    data = request.get_json()
    gemini_key = data.get('gemini_key', '').strip()
    openai_key = data.get('openai_key', '').strip()

    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')

    def is_valid_key(key):
        return key and '...' not in key and len(key) > 20

    try:
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
        else:
            content = ''

        if is_valid_key(gemini_key):
            if 'GEMINI_API_KEY=' in content:
                content = re.sub(r'GEMINI_API_KEY=.*', f'GEMINI_API_KEY={gemini_key}', content)
            else:
                content += f'\nGEMINI_API_KEY={gemini_key}'
            os.environ['GEMINI_API_KEY'] = gemini_key

        if is_valid_key(openai_key):
            if 'OPENAI_API_KEY=' in content:
                content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', content)
            else:
                content += f'\nOPENAI_API_KEY={openai_key}'
            os.environ['OPENAI_API_KEY'] = openai_key

        with open(env_path, 'w') as f:
            f.write(content)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/blog/new', methods=['GET', 'POST'])
@admin_bp.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def new_post(post_id=None):
    from app.extensions import db
    from app.models import BlogPost

    post = BlogPost.query.get_or_404(post_id) if post_id else None

    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        featured_image_url = request.form.get('featured_image_url', '')
        references = request.form.get('references', '')

        if post:
            post.title = title
            post.content = content
            post.featured_image_url = featured_image_url
            if references:
                post.references = references
        else:
            post = BlogPost(title=title, content=content)
            if hasattr(post, 'featured_image_url'):
                post.featured_image_url = featured_image_url
            if hasattr(post, 'references') and references:
                post.references = references
            db.session.add(post)

        db.session.commit()
        return redirect(url_for('public.blog'))

    return render_template('admin/new_post.html', post=post)


@admin_bp.route('/doctors')
@login_required
def admin_doctors():
    from app.models import User
    doctors = User.query.filter_by(role='doctor').all()
    return render_template('admin/doctors_list.html', doctors=doctors)


@admin_bp.route('/doctors/new', methods=['GET', 'POST'])
@login_required
def admin_doctors_new():
    from app.extensions import db
    from app.models import User, DoctorProfile

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        specialty = request.form.get('specialty')
        color = request.form.get('color')
        bio = request.form.get('bio')

        if User.query.filter_by(username=username).first():
            flash('El usuario ya existe', 'danger')
        else:
            hashed = generate_password_hash(password)
            new_user = User(username=username, password_hash=hashed, role='doctor')
            db.session.add(new_user)
            db.session.commit()

            profile = DoctorProfile(user_id=new_user.id, name=name, specialty=specialty, color=color, bio=bio)
            db.session.add(profile)
            db.session.commit()
            flash('Médico creado', 'success')
            return redirect(url_for('admin.admin_doctors'))

    return render_template('admin/doctor_form.html')


@admin_bp.route('/doctors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_doctors_edit(id):
    from app.extensions import db
    from app.models import User, DoctorProfile

    doctor_user = User.query.get_or_404(id)
    if doctor_user.role != 'doctor':
        flash('No es un médico', 'danger')
        return redirect(url_for('admin.admin_doctors'))

    profile = DoctorProfile.query.filter_by(user_id=id).first()
    if not profile:
        profile = DoctorProfile(user_id=id, name=doctor_user.username, specialty='General')
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        doctor_user.username = request.form.get('username')
        if request.form.get('password'):
            doctor_user.password_hash = generate_password_hash(request.form.get('password'))

        profile.name = request.form.get('name')
        profile.specialty = request.form.get('specialty')
        profile.bio = request.form.get('bio')
        profile.color = request.form.get('color')

        db.session.commit()
        flash('Médico actualizado', 'success')
        return redirect(url_for('admin.admin_doctors'))

    return render_template('admin/doctor_form.html', doctor=doctor_user, profile=profile)


@admin_bp.route('/doctors/<int:id>/schedule', methods=['GET', 'POST'])
@login_required
def admin_doctors_schedule(id):
    from app.extensions import db
    from app.models import User, WorkSchedule

    doctor = User.query.get_or_404(id)
    schedules = WorkSchedule.query.filter_by(doctor_id=id).order_by(WorkSchedule.day_of_week).all()
    sched_map = {s.day_of_week: s for s in schedules}

    if request.method == 'POST':
        for day in range(7):
            active = request.form.get(f'day_{day}_active') == 'on'
            start_str = request.form.get(f'day_{day}_start')
            end_str = request.form.get(f'day_{day}_end')

            s = sched_map.get(day)
            if active and start_str and end_str:
                try:
                    start_t = datetime.strptime(start_str, '%H:%M').time()
                    end_t = datetime.strptime(end_str, '%H:%M').time()
                except ValueError:
                    continue

                if not s:
                    s = WorkSchedule(doctor_id=id, day_of_week=day)
                    db.session.add(s)

                s.start_time = start_t
                s.end_time = end_t
                s.is_active = True
            else:
                if s:
                    s.is_active = False

        db.session.commit()
        flash('Horario actualizado', 'success')
        return redirect(url_for('admin.admin_doctors'))

    return render_template('admin/doctor_schedule.html', doctor=doctor, sched_map=sched_map)


@admin_bp.route('/doctors/<int:id>/delete', methods=['POST'])
@login_required
def admin_doctors_delete(id):
    from app.extensions import db
    from app.models import User, DoctorProfile, WorkSchedule, Appointment

    doctor_user = User.query.get_or_404(id)
    if doctor_user.role != 'doctor':
        flash('No es un médico', 'danger')
        return redirect(url_for('admin.admin_doctors'))

    # Nullify references in appointments
    Appointment.query.filter_by(doctor_id=id).update({'doctor_id': None})
    
    # Delete schedules
    WorkSchedule.query.filter_by(doctor_id=id).delete()
    
    # Delete profile
    profile = DoctorProfile.query.filter_by(user_id=id).first()
    if profile:
        db.session.delete(profile)
        
    # Delete the user
    db.session.delete(doctor_user)
    db.session.commit()
    
    flash('Médico eliminado correctamente', 'success')
    return redirect(url_for('admin.admin_doctors'))



@admin_bp.route('/calendario')
@login_required
def admin_calendario():
    from app.models import User, DoctorProfile
    doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
    return render_template('admin/calendario.html', doctors=doctors)


@admin_bp.route('/api/appointments')
@login_required
def api_appointments():
    from app.models import Appointment, Patient, Service
    doctor_id = request.args.get('doctor_id', type=int)
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not doctor_id:
        return jsonify({'error': 'doctor_id requerido'}), 400

    query = Appointment.query.filter_by(doctor_id=doctor_id)

    if start_str:
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        query = query.filter(Appointment.start_time >= start_date)
    if end_str:
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        query = query.filter(Appointment.start_time <= end_date)

    appointments = query.order_by(Appointment.start_time).all()

    result = []
    for appt in appointments:
        result.append({
            'id': appt.id,
            'start_time': appt.start_time.isoformat(),
            'status': appt.status,
            'patient_name': appt.patient.name if appt.patient else 'Sin nombre',
            'service_name': appt.service.name if appt.service else 'Sin servicio',
        })

    return jsonify({'appointments': result})


# --- Blog Management API Endpoints ---

@admin_bp.route('/api/posts')
@login_required
def api_list_posts():
    """Devuelve la lista de todos los blog posts."""
    from app.models import BlogPost
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify({'posts': [{
        'id': p.id,
        'title': p.title,
        'is_published': p.is_published,
        'created_at': p.created_at.strftime('%d %b, %Y') if p.created_at else ''
    } for p in posts]})


@admin_bp.route('/api/posts/<int:post_id>/toggle', methods=['POST'])
@login_required
def api_toggle_post(post_id):
    """Alterna la visibilidad de un blog post."""
    from app.extensions import db
    from app.models import BlogPost
    post = BlogPost.query.get_or_404(post_id)
    post.is_published = not post.is_published
    db.session.commit()
    return jsonify({'success': True, 'is_published': post.is_published})


@admin_bp.route('/api/posts/<int:post_id>', methods=['DELETE'])
@login_required
def api_delete_post(post_id):
    """Elimina un blog post."""
    from app.extensions import db
    from app.models import BlogPost
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})


# --- AI API Endpoints ---

@admin_bp.route('/api/research', methods=['POST'])
@login_required
def api_research():
    """Endpoint para investigar un tema usando IA."""
    from utils.ai_services import research_topic
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400
    result = research_topic(topic, model=model)
    return jsonify({'research': result})


@admin_bp.route('/api/generate-draft', methods=['POST'])
@login_required
def api_generate_draft():
    """Endpoint para generar un borrador de blog usando IA."""
    from utils.ai_services import generate_blog_draft
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    research = data.get('research', None)
    
    print(f"[DEBUG] generate-draft: topic='{topic}', model='{model}'")
    print(f"[DEBUG] research present: {research is not None}")
    if research:
        print(f"[DEBUG] research keys: {list(research.keys()) if isinstance(research, dict) else type(research)}")
    
    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400
    
    result = generate_blog_draft(topic, model=model, research=research)
    
    print(f"[DEBUG] result type: {type(result)}")
    print(f"[DEBUG] result keys: {list(result.keys()) if isinstance(result, dict) else 'NOT A DICT'}")
    if isinstance(result, dict):
        blocks = result.get('blocks', [])
        print(f"[DEBUG] blocks count: {len(blocks)}")
        if blocks:
            print(f"[DEBUG] first block: {blocks[0]}")
    
    return jsonify({'content': result})


@admin_bp.route('/api/generate-image', methods=['POST'])
@login_required
def api_generate_image():
    """Endpoint para generar imagen destacada usando DALL-E 3 o Gemini."""
    from utils.ai_services import generate_featured_image
    data = request.get_json()
    title = data.get('title', '')
    model = data.get('model', 'dall-e-3')
    
    if not title:
        return jsonify({'error': 'Título requerido'}), 400
        
    image_url = generate_featured_image(title, model=model)
    
    if image_url.startswith('error:'):
        return jsonify({'error': image_url}), 500
    return jsonify({'image_url': image_url})


@admin_bp.route('/api/ai-action', methods=['POST'])
@login_required
def api_ai_action():
    """Endpoint para acciones contextuales de IA sobre bloques."""
    from utils.ai_services import refine_block_content
    data = request.get_json()
    content = data.get('content', '')
    action = data.get('action', 'expand')
    context = data.get('context', '')
    model = data.get('model', 'gpt-4o')
    
    if not content:
        return jsonify({'error': 'Contenido requerido'}), 400
    
    result = refine_block_content(content, action, context, model=model)
    
    if result.startswith('Error:'):
        return jsonify({'error': result}), 500
    
    return jsonify({'refined_content': result})


@admin_bp.route('/api/seo-analyze', methods=['POST'])
@login_required
def api_seo_analyze():
    """Endpoint para análisis SEO en tiempo real."""
    from utils.ai_services import analyze_seo
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    keywords = data.get('keywords', [])
    
    result = analyze_seo(title, content, keywords)
    return jsonify(result)
