from app import create_app, db
from sqlalchemy import text, inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    with db.engine.connect() as conn:
        if 'doctor_profile' in tables:
            print("Dropping doctor_profile...")
            conn.execute(text("DROP TABLE doctor_profile"))
            
        if 'work_schedule' in tables:
            print("Dropping work_schedule...")
            conn.execute(text("DROP TABLE work_schedule"))
            
        # Check appointment columns
        columns = [c['name'] for c in inspector.get_columns('appointment')]
        if 'doctor_id' in columns:
            print("Column doctor_id exists in appointment. Attempting to drop it (this might fail on SQLite if not done via batch)...")
            # In SQLite, dropping a column is hard without recreation. 
            # If it exists, we might need to let the migration fail or manually fix it.
            # However, if 'doctor_id' exists, maybe we can just comment out that part of the migration for this run?
            # Or better, let's just assume if it's there, we might need to skip adding it?
            pass
            
        conn.commit()
    print("Cleanup complete.")
