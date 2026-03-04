"""
Rutas de API pública: Slots de disponibilidad.
Los endpoints de IA están en admin_bp (requieren autenticación).
"""
from flask import Blueprint, request
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/slots', methods=['POST'])
def api_get_slots():
    from app.models import Service
    from app.services.booking import get_available_slots

    data = request.get_json()
    doctor_id = data.get('doctor_id')
    service_id = data.get('service_id')
    date_str = data.get('date')

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
