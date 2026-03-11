"""
Servicios de lógica de reservas.
"""
import os
from datetime import datetime, timedelta


def get_available_slots(doctor_id, date_obj, duration_minutes):
    """
    Genera una lista de horarios de inicio disponibles (formato HH:MM)
    para un doctor y fecha específicos.
    """
    from app.models import Appointment, WorkSchedule

    day_of_week = date_obj.weekday()

    schedule = WorkSchedule.query.filter_by(
        doctor_id=doctor_id,
        day_of_week=day_of_week,
        is_active=True
    ).first()

    if not schedule:
        return []

    start_work = datetime.combine(date_obj, schedule.start_time)
    end_work = datetime.combine(date_obj, schedule.end_time)

    appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.status != 'cancelada',
        Appointment.start_time >= start_work,
        Appointment.start_time < end_work
    ).all()

    available_slots = []
    current_time = start_work
    delta_15min = timedelta(minutes=15)
    service_duration = timedelta(minutes=duration_minutes)

    while current_time + service_duration <= end_work:
        proposed_start = current_time
        proposed_end = current_time + service_duration

        is_free = True

        for appt in appointments:
            existing_duration = appt.service.duration_minutes if appt.service else 30
            appt_end = appt.start_time + timedelta(minutes=existing_duration)

            if (proposed_start < appt_end) and (proposed_end > appt.start_time):
                is_free = False
                break

        if is_free:
            available_slots.append(proposed_start.strftime('%H:%M'))

        current_time += delta_15min

    return available_slots


def check_availability(service_id, start_time, duration_minutes):
    """
    Verifica si un horario específico está disponible.
    """
    from app.models import Appointment

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


def generate_confirmation_token(email):
    """Genera un token de confirmación para el email."""
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    return serializer.dumps(email, salt='email-confirm-salt')


def confirm_token(token, expiration=3600):
    """Verifica y decodifica un token de confirmación."""
    from itsdangerous import URLSafeTimedSerializer
    serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt='email-confirm-salt',
            max_age=expiration
        )
    except Exception:
        return False
    return email
