import requests
from app import create_app
from models import User, Service
from datetime import date, timedelta

app = create_app()

def test_slots():
    with app.app_context():
        # Get data
        doctor = User.query.filter_by(role='doctor').first()
        service = Service.query.first()
        
        if not doctor or not service:
            print("Error: No doctor or service found. Did you run seed_data.py?")
            return

        print(f"Testing slots for Doctor: {doctor.username} (ID: {doctor.id})")
        print(f"Service: {service.name} (ID: {service.id}, Duration: {service.duration_minutes}m)")
        
        # Test a date (e.g., tomorrow)
        tomorrow = date.today() + timedelta(days=1)
        # Ensure tomorrow is a weekday for the test (skip if weekend to avoid empty list confusion, though our logic handles it)
        while tomorrow.weekday() > 4: # If Sat or Sun
            tomorrow += timedelta(days=1)
            
        date_str = tomorrow.strftime('%Y-%m-%d')
        print(f"Checking date: {date_str}")
        
        # Simulate API call logic directly (since we can't easily curl localhost inside this env sometimes without running server in background, 
        # but the server IS running. Let's try requests to localhost)
        
        try:
            url = "http://127.0.0.1:5000/api/slots"
            payload = {
                "doctor_id": doctor.id,
                "service_id": service.id,
                "date": date_str
            }
            
            # We need the CSRF token if we were a browser, but for API testing we might need to disable CSRF or use a testing client.
            # Using Flask test client is better.
            with app.test_client() as client:
                # Disable CSRF for testing or fetch a token first. 
                # Simpler: Just direct logic call for verification proof.
                from utils.booking_logic import get_available_slots
                slots = get_available_slots(doctor.id, tomorrow, service.duration_minutes)
                
                print(f"\n--- Available Slots ---")
                print(slots)
                
                if len(slots) > 0:
                    print("\nSUCCESS: Slots generated successfully.")
                else:
                    print("\nWARNING: No slots return. Check schedule or logic.")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    test_slots()
