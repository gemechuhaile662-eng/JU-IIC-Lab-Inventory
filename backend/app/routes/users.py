from flask import Blueprint, jsonify

users_bp = Blueprint('users', __name__)

@users_bp.route('/ping')
def ping():
    return jsonify({'module': 'users', 'status': 'ok'})