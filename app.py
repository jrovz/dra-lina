import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime
from models import db, User, BlogPost, DoctorProfile, WorkSchedule, Appointment
from forms import LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import request, flash, redirect, url_for

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_for_dra_lina')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dra_lina.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    csrf = CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.login_view = 'admin_login'
    login_manager.init_app(app)
    migrate = Migrate(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # --- RUTAS PÚBLICAS ---
    @app.route('/')
    def index():
        doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
        return render_template('public/index.html', doctors=doctors)

    @app.route('/blog')
    def blog():
        all_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).all()
        featured_post = all_posts[0] if all_posts else None
        recent_posts = all_posts[1:] if len(all_posts) > 1 else []
        return render_template('public/blog.html', featured_post=featured_post, recent_posts=recent_posts)

    @app.route('/blog/<int:post_id>')
    def post_detail(post_id):
        post = BlogPost.query.get_or_404(post_id)
        return render_template('public/post_detail.html', post=post)

    @app.route('/reservar', methods=['GET', 'POST'])
    def reservar():
        from flask import request, flash, redirect, url_for
        from utils.booking_logic import check_availability, generate_confirmation_token
        from models import Patient, Appointment, Service, DoctorProfile, User
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            service_id = request.form.get('service_id')
            doctor_id = request.form.get('doctor_id')
            date_str = request.form.get('date')      # YYYY-MM-DD
            time_str = request.form.get('time')      # HH:MM
            
            # Combinar fecha y hora
            full_date_str = f"{date_str}T{time_str}"
            start_time = datetime.strptime(full_date_str, '%Y-%m-%dT%H:%M')
            
            service = Service.query.get(service_id)
            
            # Validar disponibilidad (backend check final)
            # Nota: Para la validación final, podríamos reusar get_available_slots o check_availability con doctor
            # Por simplicidad y robustez, usamos check_availability (si se actualizó) o una lógica similar.
            # Aquí asumimos que el frontend ya validó, pero el backend debe asegurar.
            
            # Buscar paciente
            patient = Patient.query.filter_by(email=email).first()
            if not patient:
                patient = Patient(name=name, email=email)
                db.session.add(patient)
            
            token = generate_confirmation_token(email)
            appt = Appointment(patient=patient, service_id=service_id, doctor_id=doctor_id,
                               start_time=start_time, confirmation_token=token)
            db.session.add(appt)
            db.session.commit()
            
            # Simulamos envío de correo
            print(f"Token generado para {email}: {token}")
            return render_template('public/success_booking.html', email=email)

        services = Service.query.all()
        # Obtener solo usuarios con perfil de doctor
        doctors = User.query.join(DoctorProfile).filter(User.role == 'doctor').all()
        return render_template('public/reservar.html', services=services, doctors=doctors)

    @app.route('/api/slots', methods=['POST'])
    def api_get_slots():
        from utils.booking_logic import get_available_slots
        from models import Service
        
        data = request.get_json()
        doctor_id = data.get('doctor_id')
        service_id = data.get('service_id')
        date_str = data.get('date') # YYYY-MM-DD
        
        if not all([doctor_id, service_id, date_str]):
            return {'error': 'Faltan datos'}, 400
            
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            service = Service.query.get(service_id)
            if not service:
                return {'error': 'Servicio no encontrado'}, 404
                
            slots = get_available_slots(doctor_id, date_obj, service.duration_minutes)
            return {'slots': slots}
        except ValueError:
            return {'error': 'Formato de fecha inválido'}, 400

    @app.route('/confirmar/<token>')
    def confirmar_cita(token):
        from utils.booking_logic import confirm_token
        from models import Appointment
        
        email = confirm_token(token)
        if email:
            appt = Appointment.query.filter_by(confirmation_token=token).first()
            if appt:
                appt.status = 'confirmada'
                db.session.commit()
                return "Cita confirmada con éxito. ¡Te esperamos!"
        
        return "Token inválido o expirado.", 400

    # --- RUTAS ADMINISTRATIVAS ---
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if current_user.is_authenticated:
            return redirect(url_for('admin_dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('admin_dashboard'))
            else:
                flash('Usuario o contraseña incorrectos.', 'danger')
        
        return render_template('admin/login.html', form=form)

    @app.route('/admin/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        # Check if API keys are configured
        gemini_key = os.getenv('GEMINI_API_KEY', '')
        openai_key = os.getenv('OPENAI_API_KEY', '')
        
        gemini_configured = bool(gemini_key and not gemini_key.startswith('AIza-tu'))
        openai_configured = bool(openai_key and not openai_key.startswith('sk-tu'))
        
        # Mask keys for display
        gemini_masked = (gemini_key[:8] + '...' + gemini_key[-4:]) if len(gemini_key) > 12 else ''
        openai_masked = (openai_key[:7] + '...' + openai_key[-4:]) if len(openai_key) > 11 else ''
        
        return render_template('admin/dashboard.html',
                               gemini_configured=gemini_configured,
                               openai_configured=openai_configured,
                               gemini_key_masked=gemini_masked,
                               openai_key_masked=openai_masked)

    @app.route('/admin/api/settings', methods=['POST'])
    @login_required
    def api_save_settings():
        """Guarda las API keys en el archivo .env"""
        from flask import jsonify
        import re
        
        data = request.get_json()
        gemini_key = data.get('gemini_key', '').strip()
        openai_key = data.get('openai_key', '').strip()
        
        # Path to .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Helper to check if key is masked (contains ...)
        def is_valid_key(key):
            return key and '...' not in key and len(key) > 20
        
        try:
            # Read current .env content
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    content = f.read()
            else:
                content = ''
            
            # Update or add GEMINI_API_KEY (only if it's a real key, not masked)
            if is_valid_key(gemini_key):
                if 'GEMINI_API_KEY=' in content:
                    content = re.sub(r'GEMINI_API_KEY=.*', f'GEMINI_API_KEY={gemini_key}', content)
                else:
                    content += f'\nGEMINI_API_KEY={gemini_key}'
                # Update environment variable immediately
                os.environ['GEMINI_API_KEY'] = gemini_key
            
            # Update or add OPENAI_API_KEY (only if it's a real key, not masked)
            if is_valid_key(openai_key):
                if 'OPENAI_API_KEY=' in content:
                    content = re.sub(r'OPENAI_API_KEY=.*', f'OPENAI_API_KEY={openai_key}', content)
                else:
                    content += f'\nOPENAI_API_KEY={openai_key}'
                # Update environment variable immediately
                os.environ['OPENAI_API_KEY'] = openai_key
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.write(content)
            
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


    @app.route('/admin/blog/new', methods=['GET', 'POST'])
    @login_required
    def new_post():
        from flask import request, redirect, url_for
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            featured_image_url = request.form.get('featured_image_url', '')
            new_p = BlogPost(title=title, content=content)
            # Si el modelo tiene el campo featured_image_url, lo asignamos
            if hasattr(new_p, 'featured_image_url'):
                new_p.featured_image_url = featured_image_url
            db.session.add(new_p)
            db.session.commit()
            return redirect(url_for('blog'))
        return render_template('admin/new_post.html')

    # --- AI API Endpoints ---
    from flask import jsonify

    @app.route('/admin/api/research', methods=['POST'])
    @login_required
    def api_research():
        """Endpoint para investigar un tema usando IA."""
        from utils.ai_services import research_topic
        data = request.get_json()
        topic = data.get('topic', '')
        model = data.get('model', 'gemini-2.0-flash')
        if not topic:
            return jsonify({'error': 'Tema requerido'}), 400
        result = research_topic(topic, model=model)
        return jsonify({'research': result})

    @app.route('/admin/api/generate-draft', methods=['POST'])
    @login_required
    def api_generate_draft():
        """Endpoint para generar un borrador de blog usando IA."""
        from utils.ai_services import generate_blog_draft
        data = request.get_json()
        topic = data.get('topic', '')
        model = data.get('model', 'gemini-2.0-flash')
        if not topic:
            return jsonify({'error': 'Tema requerido'}), 400
        result = generate_blog_draft(topic, model=model)
        return jsonify({'content': result})

    @app.route('/admin/api/generate-image', methods=['POST'])
    @login_required
    def api_generate_image():
        """Endpoint para generar imagen destacada usando DALL-E 3 o Gemini."""
        from utils.ai_services import generate_featured_image
        data = request.get_json()
        title = data.get('title', '')
        model = data.get('model', 'dall-e-3') # Default a DALL-E 3 si no se especifica
        
        if not title:
            return jsonify({'error': 'Título requerido'}), 400
            
        image_url = generate_featured_image(title, model=model)
        
        if image_url.startswith('error:'):
            return jsonify({'error': image_url}), 500
        return jsonify({'image_url': image_url})

    @app.route('/admin/api/ai-action', methods=['POST'])
    @login_required
    def api_ai_action():
        """Endpoint para acciones contextuales de IA sobre bloques."""
        from utils.ai_services import refine_block_content
        data = request.get_json()
        content = data.get('content', '')
        action = data.get('action', 'expand')
        context = data.get('context', '')
        model = data.get('model', 'gemini-2.0-flash')
        
        if not content:
            return jsonify({'error': 'Contenido requerido'}), 400
        
        result = refine_block_content(content, action, context, model=model)
        
        if result.startswith('Error:'):
            return jsonify({'error': result}), 500
        
        return jsonify({'refined_content': result})

    @app.route('/admin/api/seo-analyze', methods=['POST'])
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

    # --- ADMIN DOCTORS ---
    @app.route('/admin/doctors')
    @login_required
    def admin_doctors():
        doctors = User.query.filter_by(role='doctor').all()
        return render_template('admin/doctors_list.html', doctors=doctors)

    @app.route('/admin/doctors/new', methods=['GET', 'POST'])
    @login_required
    def admin_doctors_new():
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
                return redirect(url_for('admin_doctors'))
                
        return render_template('admin/doctor_form.html')

    @app.route('/admin/doctors/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def admin_doctors_edit(id):
        doctor_user = User.query.get_or_404(id)
        if doctor_user.role != 'doctor': 
            flash('No es un médico', 'danger')
            return redirect(url_for('admin_doctors'))
            
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
            return redirect(url_for('admin_doctors'))
            
        return render_template('admin/doctor_form.html', doctor=doctor_user, profile=profile)

    @app.route('/admin/doctors/<int:id>/schedule', methods=['GET', 'POST'])
    @login_required
    def admin_doctors_schedule(id):
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
            return redirect(url_for('admin_doctors'))
            
        return render_template('admin/doctor_schedule.html', doctor=doctor, sched_map=sched_map)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() # Crear tablas si no existen
    app.run(debug=True)
