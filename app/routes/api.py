"""
Rutas de API: Slots, IA, SEO.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required
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


@api_bp.route('/research', methods=['POST'])
@login_required
def api_research():
    from app.services.ai_service import research_topic
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400
    result = research_topic(topic, model=model)
    return jsonify({'research': result})


@api_bp.route('/generate-draft', methods=['POST'])
@login_required
def api_generate_draft():
    from app.services.ai_service import generate_blog_draft
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400
    result = generate_blog_draft(topic, model=model)
    return jsonify({'content': result})


@api_bp.route('/generate-image', methods=['POST'])
@login_required
def api_generate_image():
    from app.services.ai_service import generate_featured_image
    data = request.get_json()
    title = data.get('title', '')
    model = data.get('model', 'dall-e-3')

    if not title:
        return jsonify({'error': 'Título requerido'}), 400

    image_url = generate_featured_image(title, model=model)

    if image_url.startswith('error:'):
        return jsonify({'error': image_url}), 500
    return jsonify({'image_url': image_url})


@api_bp.route('/ai-action', methods=['POST'])
@login_required
def api_ai_action():
    from app.services.ai_service import refine_block_content
    data = request.get_json()
    content = data.get('content', '')
    action = data.get('action', 'expand')
    context = data.get('context', '')
    model = data.get('model', 'gpt-4o')

    if not content:
        return jsonify({'error': 'Contenido requerido'}), 400

    result = refine_block_content(content, action, context, model=model)

    if result.startswith('Error:'):
        return jsonify({'error': result}), 500

    return jsonify({'refined_content': result})


@api_bp.route('/seo-analyze', methods=['POST'])
@login_required
def api_seo_analyze():
    from app.services.ai_service import analyze_seo
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    keywords = data.get('keywords', [])

    result = analyze_seo(title, content, keywords)
    return jsonify(result)
