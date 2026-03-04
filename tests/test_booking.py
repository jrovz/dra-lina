"""
Tests for booking logic: slot availability and overlap detection.
"""
from datetime import datetime, time, timedelta


def test_get_available_slots_no_schedule(app, db_session):
    """When a doctor has no schedule for a given day, returns empty list."""
    from app.services.booking import get_available_slots
    from app.models import User
    from werkzeug.security import generate_password_hash

    doctor = User(username='dr_test_slots', password_hash=generate_password_hash('pass'), role='doctor')
    db_session.add(doctor)
    db_session.commit()

    date_obj = datetime(2026, 3, 10).date()  # A Tuesday
    slots = get_available_slots(doctor.id, date_obj, 30)
    assert slots == []


def test_get_available_slots_with_schedule(app, db_session):
    """Returns available slots when doctor has a schedule and no appointments."""
    from app.services.booking import get_available_slots
    from app.models import User, WorkSchedule
    from werkzeug.security import generate_password_hash

    doctor = User(username='dr_test_free', password_hash=generate_password_hash('pass'), role='doctor')
    db_session.add(doctor)
    db_session.commit()

    schedule = WorkSchedule(
        doctor_id=doctor.id,
        day_of_week=0,  # Monday
        start_time=time(9, 0),
        end_time=time(10, 0),
        is_active=True
    )
    db_session.add(schedule)
    db_session.commit()

    date_obj = datetime(2026, 3, 9).date()  # A Monday
    slots = get_available_slots(doctor.id, date_obj, 30)
    assert len(slots) > 0
    assert '09:00' in slots


def test_get_available_slots_blocked_by_appointment(app, db_session):
    """Existing appointment blocks overlapping slots."""
    from app.services.booking import get_available_slots
    from app.models import User, WorkSchedule, Service, Patient, Appointment
    from werkzeug.security import generate_password_hash

    doctor = User(username='dr_test_busy', password_hash=generate_password_hash('pass'), role='doctor')
    db_session.add(doctor)
    db_session.commit()

    schedule = WorkSchedule(
        doctor_id=doctor.id,
        day_of_week=0,
        start_time=time(9, 0),
        end_time=time(10, 0),
        is_active=True
    )
    service = Service(name='Consulta General', duration_minutes=30, price=50.0)
    patient = Patient(name='Test Patient', document_id='123456', phone='555-0000', age=30)
    db_session.add_all([schedule, service, patient])
    db_session.commit()

    appointment = Appointment(
        patient_id=patient.id,
        service_id=service.id,
        doctor_id=doctor.id,
        start_time=datetime(2026, 3, 9, 9, 0),
        status='confirmada'
    )
    db_session.add(appointment)
    db_session.commit()

    date_obj = datetime(2026, 3, 9).date()
    slots = get_available_slots(doctor.id, date_obj, 30)
    assert '09:00' not in slots
    assert '09:15' not in slots
    assert '09:30' in slots


def test_check_availability_free(app, db_session):
    """Returns True when no overlapping appointment exists."""
    from app.services.booking import check_availability

    start = datetime(2026, 3, 15, 14, 0)
    assert check_availability(1, start, 30) is True


def test_check_availability_overlap(app, db_session):
    """Returns False when an overlapping appointment exists."""
    from app.services.booking import check_availability
    from app.models import Service, Patient, Appointment
    from werkzeug.security import generate_password_hash

    service = Service(name='Check', duration_minutes=30, price=30.0)
    patient = Patient(name='Overlap Patient', document_id='999888', phone='555-1111', age=25)
    db_session.add_all([service, patient])
    db_session.commit()

    appointment = Appointment(
        patient_id=patient.id,
        service_id=service.id,
        start_time=datetime(2026, 3, 15, 14, 0),
        status='confirmada'
    )
    db_session.add(appointment)
    db_session.commit()

    assert check_availability(service.id, datetime(2026, 3, 15, 14, 15), 30) is False
