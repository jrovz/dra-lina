from app import create_app, db
from models import BlogPost, User
from datetime import datetime
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Crear un usuario admin si no existe
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password_hash=generate_password_hash('admin123')) 
        db.session.add(admin)
        db.session.commit()

    # Artículos de ejemplo
    articulos = [
        {
            "title": "Guía Definitiva para la Salud Familiar en 2025",
            "content": "El bienestar de la familia comienza con hábitos preventivos. En este artículo exploramos cómo mantener a todos sanos...",
        },
        {
            "title": "La importancia del chequeo anual preventivo",
            "content": "Prevenir es mejor que curar. Un chequeo anual puede detectar problemas antes de que se vuelvan graves.",
        },
        {
            "title": "Consejos de nutrición para todas las edades",
            "content": "Desde los más pequeños hasta los abuelos, la alimentación es la base de una vida plena.",
        },
        {
            "title": "Cuidado del corazón en el hogar",
            "content": "Pequeños cambios en la rutina diaria pueden tener un gran impacto en nuestra salud cardiovascular.",
        }
    ]

    for art in articulos:
        if not BlogPost.query.filter_by(title=art['title']).first():
            post = BlogPost(title=art['title'], content=art['content'], author_id=admin.id)
            db.session.add(post)
    
    db.session.commit()
    print("Base de datos poblada con éxito.")
