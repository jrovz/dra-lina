"""
Task status polling endpoint for async Celery tasks.
"""
from flask import jsonify
from flask_jwt_extended import jwt_required
from . import api_v1_bp


@api_v1_bp.route('/tasks/<task_id>')
@jwt_required()
def get_task_status(task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'state': result.state,
    }

    if result.state == 'PENDING':
        response['status'] = 'Tarea en cola...'
    elif result.state == 'STARTED':
        response['status'] = 'Procesando...'
    elif result.state == 'SUCCESS':
        response['status'] = 'Completado'
        response['result'] = result.result
    elif result.state == 'FAILURE':
        response['status'] = 'Error'
        response['error'] = str(result.info)
    else:
        response['status'] = str(result.state)

    return jsonify(response)
