import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from dotenv import load_dotenv
from datetime import datetime
from models import db, User, BlogPost
from forms import LoginForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
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
        return render_template('public/index.html')

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
        from models import Patient, Appointment, Service
        
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            service_id = request.form.get('service_id')
            date_str = request.form.get('date') # Formato: YYYY-MM-DDTHH:MM
            
            start_time = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
            service = Service.query.get(service_id)
            
            if check_availability(service_id, start_time, service.duration_minutes):
                # Crear o buscar paciente
                patient = Patient.query.filter_by(email=email).first()
                if not patient:
                    patient = Patient(name=name, email=email)
                    db.session.add(patient)
                
                token = generate_confirmation_token(email)
                appt = Appointment(patient=patient, service_id=service_id, 
                                   start_time=start_time, confirmation_token=token)
                db.session.add(appt)
                db.session.commit()
                
                # Aquí se enviaría el correo con Flask-Mail
                print(f"Token generado para {email}: {token}")
                return "Cita solicitada. Por favor revisa tu correo para confirmar."
            else:
                return "Horario no disponible. Intenta con otro.", 400
                
        services = Service.query.all()
        return render_template('public/reservar.html', services=services)

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
        return render_template('admin/dashboard.html')

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
        if not topic:
            return jsonify({'error': 'Tema requerido'}), 400
        result = research_topic(topic)
        return jsonify({'research': result})

    @app.route('/admin/api/generate-draft', methods=['POST'])
    @login_required
    def api_generate_draft():
        """Endpoint para generar un borrador de blog usando IA."""
        from utils.ai_services import generate_blog_draft
        data = request.get_json()
        topic = data.get('topic', '')
        if not topic:
            return jsonify({'error': 'Tema requerido'}), 400
        result = generate_blog_draft(topic)
        return jsonify({'content': result})

    @app.route('/admin/api/generate-image', methods=['POST'])
    @login_required
    def api_generate_image():
        """Endpoint para generar imagen destacada usando DALL-E 3."""
        from utils.ai_services import generate_featured_image
        data = request.get_json()
        title = data.get('title', '')
        if not title:
            return jsonify({'error': 'Título requerido'}), 400
        image_url = generate_featured_image(title)
        if image_url.startswith('error:'):
            return jsonify({'error': image_url}), 500
        return jsonify({'image_url': image_url})

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all() # Crear tablas si no existen
    app.run(debug=True)
