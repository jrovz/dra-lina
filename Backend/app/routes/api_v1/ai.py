"""
AI API v1 endpoints with rate limiting and async task support.
All endpoints require JWT authentication.
"""
import logging
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp
from app.extensions import limiter

logger = logging.getLogger(__name__)


@api_v1_bp.route('/ai/research', methods=['POST'])
@jwt_required()
@limiter.limit('10/hour')
def ai_research():
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    async_mode = data.get('async', False)

    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400

    if async_mode:
        from app.tasks import research_topic_task
        task = research_topic_task.delay(topic, model)
        return jsonify({'task_id': task.id, 'status': 'PENDING'}), 202

    from utils.ai_services import research_topic
    result = research_topic(topic, model=model)
    return jsonify({'research': result})


@api_v1_bp.route('/ai/generate-draft', methods=['POST'])
@jwt_required()
@limiter.limit('10/hour')
def ai_generate_draft():
    data = request.get_json()
    topic = data.get('topic', '')
    model = data.get('model', 'gpt-4o')
    research = data.get('research')
    async_mode = data.get('async', False)

    if not topic:
        return jsonify({'error': 'Tema requerido'}), 400

    if async_mode:
        from app.tasks import generate_draft_task
        task = generate_draft_task.delay(topic, model, research)
        return jsonify({'task_id': task.id, 'status': 'PENDING'}), 202

    from utils.ai_services import generate_blog_draft
    result = generate_blog_draft(topic, model=model, research=research)
    return jsonify({'content': result})


@api_v1_bp.route('/ai/generate-image', methods=['POST'])
@jwt_required()
@limiter.limit('5/hour')
def ai_generate_image():
    data = request.get_json()
    title = data.get('title', '')
    model = data.get('model', 'dall-e-3')
    async_mode = data.get('async', False)

    if not title:
        return jsonify({'error': 'Título requerido'}), 400

    if async_mode:
        from app.tasks import generate_image_task
        task = generate_image_task.delay(title, model)
        return jsonify({'task_id': task.id, 'status': 'PENDING'}), 202

    from utils.ai_services import generate_featured_image
    image_url = generate_featured_image(title, model=model)

    if image_url.startswith('error:'):
        return jsonify({'error': image_url}), 500
    return jsonify({'image_url': image_url})


@api_v1_bp.route('/ai/refine-block', methods=['POST'])
@jwt_required()
@limiter.limit('30/hour')
def ai_refine_block():
    data = request.get_json()
    content = data.get('content', '')
    action = data.get('action', 'expand')
    context = data.get('context', '')
    model = data.get('model', 'gpt-4o')

    if not content:
        return jsonify({'error': 'Contenido requerido'}), 400

    from utils.ai_services import refine_block_content
    result = refine_block_content(content, action, context, model=model)

    if result.startswith('Error:'):
        return jsonify({'error': result}), 500
    return jsonify({'refined_content': result})


@api_v1_bp.route('/ai/seo-analyze', methods=['POST'])
@jwt_required()
@limiter.limit('30/hour')
def ai_seo_analyze():
    data = request.get_json()
    title = data.get('title', '')
    content = data.get('content', '')
    keywords = data.get('keywords', [])

    from utils.ai_services import analyze_seo
    result = analyze_seo(title, content, keywords)
    return jsonify(result)
