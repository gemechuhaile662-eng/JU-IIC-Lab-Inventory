# =========================================================
# app/routes/recognize.py
# POST /api/recognize         — photo → item info
# POST /api/recognition/correct — log correction
# GET  /api/recognition/recent  — last N scans
# =========================================================

import os
import uuid
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app

from app import db
from app.models import (
    Equipment, Component, ItemClass,
    RecognitionLog, RecognitionCorrection
)
from app.services.recognizer import get_recognizer

recognize_bp = Blueprint('recognize', __name__)


def _save_upload(file):
    """Save uploaded file to /uploads with a unique name. Returns path."""
    ext = os.path.splitext(file.filename)[1] or '.jpg'
    name = f'{uuid.uuid4().hex}{ext}'
    folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    file.save(path)
    return path, name


def _lookup_item(item_type, item_id):
    """Fetch the equipment/component row and join lab/supplier."""
    if item_type == 'equipment':
        item = Equipment.query.get(item_id)
        if not item:
            return None
        return {
            'item_type': 'equipment',
            'item_id': item.equip_id,
            'display_name': item.equip_name,
            'lab_name': item.laboratory.lab_name if item.laboratory else None,
            'supplier_name': item.supplier.supplier_name if item.supplier else None,
            'unit_price': float(item.unit_price) if item.unit_price else None,
            'status': item.status,
            'asset_tag': item.asset_tag,
            'serial_no': item.serial_no,
            'quantity': None,
            'low_stock': False,
            'last_txn_date': None,
        }
    elif item_type == 'component':
        item = Component.query.get(item_id)
        if not item:
            return None
        return {
            'item_type': 'component',
            'item_id': item.comp_id,
            'display_name': item.comp_name,
            'lab_name': item.laboratory.lab_name if item.laboratory else None,
            'supplier_name': item.supplier.supplier_name if item.supplier else None,
            'unit_price': float(item.unit_price) if item.unit_price else None,
            'status': None,
            'asset_tag': None,
            'serial_no': None,
            'quantity': item.quantity,
            'unit': item.unit,
            'low_stock': item.low_stock,
            'last_txn_date': None,
        }
    return None


# =========================================================
# POST /api/recognize
# =========================================================
@recognize_bp.route('/recognize', methods=['POST'])
def recognize():
    if 'image' not in request.files:
        return jsonify({'error': 'no image uploaded'}), 400

    file = request.files['image']
    if not file or not file.filename:
        return jsonify({'error': 'empty image'}), 400

    # Save upload
    try:
        path, fname = _save_upload(file)
    except Exception as e:
        return jsonify({'error': f'upload failed: {e}'}), 500

    # Predict
    rec = get_recognizer(current_app.config.get('MODEL_PATH'))
    class_name, confidence = rec.predict(path)

    # Find item_classes row
    ic = ItemClass.query.filter_by(class_name=class_name).first() if class_name else None

    # Decide status based on confidence
    success_thresh = current_app.config.get('CONFIDENCE_SUCCESS', 0.75)
    low_thresh = current_app.config.get('CONFIDENCE_LOW', 0.40)

    if ic is None or confidence < low_thresh:
        status = 'unknown_item'
    elif confidence < success_thresh:
        status = 'low_confidence'
    else:
        status = 'success'

    # Log it
    log = RecognitionLog(
        user_id=None,                     # no auth yet
        image_path=fname,
        detected_class_id=ic.class_id if ic else None,
        confidence=confidence,
        item_type=ic.item_type if ic else None,
        item_id=ic.item_id if ic else None,
        result_status=status,
        photo_date=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    # Build response
    payload = {
        'log_id': log.log_id,
        'result_status': status,
        'class_id': ic.class_id if ic else None,
        'confidence': round(confidence, 4),
    }

    if status == 'success' and ic:
        item_info = _lookup_item(ic.item_type, ic.item_id)
        if item_info:
            payload.update(item_info)

    return jsonify(payload), 200


# =========================================================
# POST /api/recognition/correct
# =========================================================
@recognize_bp.route('/recognition/correct', methods=['POST'])
def correct():
    data = request.get_json(silent=True) or {}
    log_id = data.get('log_id')
    correct_item_type = data.get('correct_item_type')
    correct_item_id = data.get('correct_item_id')

    if not log_id:
        return jsonify({'error': 'log_id required'}), 400

    log = RecognitionLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'log not found'}), 404

    # Find the ItemClass matching (type, id)
    correct_class = ItemClass.query.filter_by(
        item_type=correct_item_type, item_id=correct_item_id
    ).first()

    corr = RecognitionCorrection(
        log_id=log_id,
        predicted_class_id=log.detected_class_id,
        correct_class_id=correct_class.class_id if correct_class else None,
        corrected_by=None,
        corrected_at=datetime.utcnow(),
    )
    log.result_status = 'user_corrected'
    db.session.add(corr)
    db.session.commit()

    return jsonify({
        'correction_id': corr.correction_id,
        'status': 'recorded'
    }), 200


# =========================================================
# GET /api/recognition/recent?limit=5
# =========================================================
@recognize_bp.route('/recognition/recent', methods=['GET'])
def recent():
    limit = int(request.args.get('limit', 5))
    logs = RecognitionLog.query.order_by(RecognitionLog.photo_date.desc()).limit(limit).all()

    results = []
    for log in logs:
        info = _lookup_item(log.item_type, log.item_id) if log.item_type else None
        results.append({
            'log_id': log.log_id,
            'image_path': f'/uploads/{log.image_path}' if log.image_path else None,
            'display_name': info['display_name'] if info else 'Unknown',
            'photo_date': log.photo_date.isoformat(),
            'result_status': log.result_status,
            'confidence': log.confidence,
        })

    return jsonify(results), 200