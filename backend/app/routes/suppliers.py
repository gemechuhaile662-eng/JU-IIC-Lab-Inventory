from flask import Blueprint, jsonify

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/ping')
def ping():
    return jsonify({'module': 'suppliers', 'status': 'ok'})