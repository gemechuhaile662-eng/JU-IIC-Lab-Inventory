from flask import Blueprint, jsonify

labs_bp = Blueprint('labs', __name__)

@labs_bp.route('/ping')
def ping():
    return jsonify({'module': 'labs', 'status': 'ok'})