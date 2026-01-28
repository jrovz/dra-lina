from datetime import datetime, timedelta, time
import os
from models import Appointment, WorkSchedule, Service

def get_available_slots(doctor_id, date_obj, duration_minutes):
    """
    Genera una lista de horarios de inicio disponibles (formato HH:MM)
    para un doctor y fecha específicos, considerando:
    - Horario de trabajo del doctor (WorkSchedule).
    - Citas existentes (Appointment) y sus duraciones reales.
    - Duración del servicio solicitado.
    - Slots de 15 minutos.
    """
    # 1. Obtener horario de trabajo para el día de la semana
    day_of_week = date_obj.weekday() # 0=Monday, 6=Sunday
    
    # Busca horario activo
    schedule = WorkSchedule.query.filter_by(
        doctor_id=doctor_id, 
        day_of_week=day_of_week, 
        is_active=True
    ).first()
    
    if not schedule:
        return [] # No trabaja este día
        
    start_work = datetime.combine(date_obj, schedule.start_time)
    end_work = datetime.combine(date_obj, schedule.end_time)
    
    # 2. Obtener citas existentes para ese doctor en ese rango
    # Ampliamos un poco el rango de búsqueda para solapamientos en bordes
    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status != 'cancelada',
        Appointment.start_time >= start_work,
        Appointment.start_time < end_work
    ).all()
    
    # 3. Generar slots candidatos
    available_slots = []
    
    # Iteramos cada 15 min desde el incio hasta el fin del turno
    current_time = start_work
    delta_15min = timedelta(minutes=15)
    service_duration = timedelta(minutes=duration_minutes)
    
    while current_time + service_duration <= end_work:
        proposed_start = current_time
        proposed_end = current_time + service_duration
        
        is_free = True
        
        # Verificar contra todas las citas existentes
        for appt in appointments:
            # Determinar fin de la cita existente
            # Si el appointment tiene service asociado, usamos su duración.
            # Si no, asumimos 30 min por seguridad.
            existing_duration = appt.service.duration_minutes if appt.service else 30
            appt_end = appt.start_time + timedelta(minutes=existing_duration)
            
            # Lógica de solapamiento:
            # (StartA < EndB) y (EndA > StartB)
            if (proposed_start < appt_end) and (proposed_end > appt.start_time):
                is_free = False
                break
        
        if is_free:
            available_slots.append(proposed_start.strftime('%H:%M'))
            
        current_time += delta_15min
        
    return available_slots

def check_availability(service_id, start_time, duration_minutes):
    """
    Legacy helper or simple check using the new logical base.
    Verify if a SPECIFIC time is available (used by backend validation).
    """
    # Necesitamos el doctor_id. En el sistema legacy /reservar actual no se pasa doctor_id explícto
    # en el POST form si no actualizamos el frontend.
    # Si mantenemos compatibilidad, buscamos 'cualquier médico' o el default (Dra Lina).
    # Por ahora, asumiremos que si no hay doctor, falla o usa uno default.
    # Pero para no romper 'reservar', mantendremos una lógica que verifique solapamientos globales 
    # si no se ha migrado todo.
    
    # Lógica SIMPLE legacy (sin doctor): revisa globalmente (como antes)
    # PERO usando duraciones reales.
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    overlapping = Appointment.query.filter(
        Appointment.status != 'cancelada',
        Appointment.start_time < end_time
    ).all()
    
    for appt in overlapping:
        existing_duration = appt.service.duration_minutes if appt.service else 30
        appt_end = appt.start_time + timedelta(minutes=existing_duration)
        
        if start_time < appt_end and end_time > appt.start_time:
            return False
            
    return True

# --- TOKEN UTILS ---

def generate_confirmation_token(email):
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    return serializer.dumps(email, salt='email-confirm-salt')

def confirm_token(token, expiration=3600):
    from itsdangerous import URLSafeTimedSerializer
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
