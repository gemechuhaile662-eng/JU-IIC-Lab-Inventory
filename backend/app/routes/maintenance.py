from flask import Blueprint, jsonify

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('/ping')
def ping():
    return jsonify({'module': 'maintenance', 'status': 'ok'})