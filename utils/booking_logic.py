from datetime import datetime, timedelta
from models import Appointment

def check_availability(service_id, start_time, duration_minutes):
    """
    Verifica si hay overbooking para un horario solicitado.
    """
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    # Buscar citas que se solapen
    overlapping = Appointment.query.filter(
        Appointment.status != 'cancelada',
        Appointment.start_time < end_time,
        # (Start A < End B) AND (End A > Start B) es la fórmula de solapamiento
    ).all()
    
    for appt in overlapping:
        # Calculamos el fin de la cita existente (asumiendo que duran lo mismo por ahora)
        # O podríamos guardar el end_time en la DB para mayor precisión
        appt_end = appt.start_time + timedelta(minutes=duration_minutes) 
        if start_time < appt_end and end_time > appt.start_time:
            return False
            
    return True

def generate_confirmation_token(email):
    from itsdangerous import URLSafeTimedSerializer
    import os
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    from itsdangerous import URLSafeTimedSerializer
    import os
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
    except:
        return False
    return email
