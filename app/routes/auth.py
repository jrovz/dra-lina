"""
Autenticación JWT: login, refresh, logout, me.
"""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from werkzeug.security import check_password_hash

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# In-memory blocklist for revoked tokens (sufficient for single-instance VPS)
BLOCKLIST = set()


@auth_bp.route('/login', methods=['POST'])
def login():
    from app.models import User
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Usuario y contraseña requeridos'}), 400

    user = User.query.filter_by(username=data['username']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    logger.info("User %s logged in via JWT", user.username)
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
    })


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token})


@auth_bp.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    BLOCKLIST.add(jti)
    return jsonify({'message': 'Token revocado'})


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    from app.models import User
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'email': user.email
    })
