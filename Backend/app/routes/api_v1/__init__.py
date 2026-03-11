"""
API v1 Blueprint.
"""
from flask import Blueprint

api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

from . import public, admin, ai, tasks_status  # noqa: E402, F401
