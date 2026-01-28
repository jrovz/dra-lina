from app import create_app, db
from models import User, DoctorProfile, WorkSchedule, Service
from werkzeug.security import generate_password_hash
from datetime import time

app = create_app()

def seed():
    with app.app_context():
        print("Seeding database...")
        
        # 1. Services
        services_data = [
            {'name': 'Consulta General', 'duration': 30, 'price': 50.0},
            {'name': 'Control Prenatal', 'duration': 45, 'price': 70.0},
            {'name': 'Ecografía', 'duration': 60, 'price': 100.0}
        ]
        
        for s_data in services_data:
            s = Service.query.filter_by(name=s_data['name']).first()
            if not s:
                s = Service(name=s_data['name'], duration_minutes=s_data['duration'], price=s_data['price'])
                db.session.add(s)
                print(f"Created Service: {s.name}")
        
        # 2. Doctors
        doctors_data = [
            {
                'name': 'Dra. Lina María',
                'username': 'dralina',
                'specialty': 'Ginecología y Obstetricia',
                'bio': 'Especialista en cuidado materno con más de 10 años de experiencia.',
                'color': '#ec4899' # Pink
            },
            {
                'name': 'Dr. Carlos Ruiz',
                'username': 'drcarlos',
                'specialty': 'Medicina General',
                'bio': 'Enfoque integral en salud familiar y preventiva.',
                'color': '#3b82f6' # Blue
            }
        ]
        
        for doc_data in doctors_data:
            user = User.query.filter_by(username=doc_data['username']).first()
            if not user:
                hashed = generate_password_hash('password123')
                user = User(username=doc_data['username'], password_hash=hashed, role='doctor')
                db.session.add(user)
                db.session.flush() # get ID
                
                profile = DoctorProfile(
                    user_id=user.id,
                    name=doc_data['name'],
                    specialty=doc_data['specialty'],
                    bio=doc_data['bio'],
                    color=doc_data['color']
                )
                db.session.add(profile)
                print(f"Created Doctor: {doc_data['name']}")
                
                # 3. Schedule (Mon-Fri, 09:00 - 17:00)
                for day in range(5): # 0=Mon to 4=Fri
                    sch = WorkSchedule(
                        doctor_id=user.id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        is_active=True
                    )
                    db.session.add(sch)
                print(f"Created Schedule for {doc_data['name']}")
                
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
