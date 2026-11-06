# =========================================================
# app/routes/items.py
# GET /api/items                        — all items
# GET /api/items/<type>/<id>            — single item detail
# GET /api/items/<type>/<id>/qr         — QR code PNG for one item
# GET /api/items/lookup/qr/<code>       — find item by QR code string
# =========================================================

import io
import zipfile

from flask import Blueprint, jsonify, send_file, Response

from app.models import Equipment, Component
from app.services.qr_service import qr_for_item, generate_qr_bytes

items_bp = Blueprint('items', __name__)


# =========================================================
# GET /api/items  — flat list of all equipment + components
# =========================================================
@items_bp.route('', methods=['GET'])
def list_items():
    items = []

    for e in Equipment.query.all():
        items.append({
            'id': e.equip_id,
            'item_type': 'equipment',
            'name': e.equip_name,
            'asset_tag': e.asset_tag,
            'qr_code': e.qr_code,
        })

    for c in Component.query.all():
        items.append({
            'id': c.comp_id,
            'item_type': 'component',
            'name': c.comp_name,
            'asset_tag': None,
            'qr_code': c.qr_code,
        })

    return jsonify(items), 200


# =========================================================
# GET /api/items/lookup/qr/<code>  — find item by QR code string
# =========================================================
# NOTE: this must come BEFORE the /<type>/<id> route,
#       otherwise Flask would match 'lookup' as item_type.
@items_bp.route('/lookup/qr/<code>', methods=['GET'])
def lookup_by_qr(code):
    # Try equipment first
    e = Equipment.query.filter_by(qr_code=code).first()
    if e:
        return jsonify({
            'item_type': 'equipment',
            'item_id': e.equip_id,
            'display_name': e.equip_name,
            'asset_tag': e.asset_tag,
            'qr_code': e.qr_code,
        }), 200

    # Then components
    c = Component.query.filter_by(qr_code=code).first()
    if c:
        return jsonify({
            'item_type': 'component',
            'item_id': c.comp_id,
            'display_name': c.comp_name,
            'asset_tag': None,
            'qr_code': c.qr_code,
        }), 200

    # Also accept "<type>:<id>" format
    if ':' in code:
        t, _, id_str = code.partition(':')
        try:
            iid = int(id_str)
        except ValueError:
            return jsonify({'error': 'invalid QR payload'}), 400

        if t == 'equipment':
            e = Equipment.query.get(iid)
            if e:
                return jsonify({
                    'item_type': 'equipment',
                    'item_id': e.equip_id,
                    'display_name': e.equip_name,
                    'asset_tag': e.asset_tag,
                    'qr_code': e.qr_code,
                }), 200
        elif t == 'component':
            c = Component.query.get(iid)
            if c:
                return jsonify({
                    'item_type': 'component',
                    'item_id': c.comp_id,
                    'display_name': c.comp_name,
                    'asset_tag': None,
                    'qr_code': c.qr_code,
                }), 200

    return jsonify({'error': 'no item found for this QR code'}), 404


# =========================================================
# GET /api/items/<type>/<id>/qr  — QR PNG for one item
# =========================================================
@items_bp.route('/<item_type>/<int:item_id>/qr', methods=['GET'])
def get_qr(item_type, item_id):
    if item_type not in ('equipment', 'component'):
        return jsonify({'error': 'invalid item_type'}), 400

    png = qr_for_item(item_type, item_id)
    return Response(png, mimetype='image/png')


# =========================================================
# GET /api/items/qr/batch  — ZIP with all QR codes
# =========================================================
@items_bp.route('/qr/batch', methods=['GET'])
def batch_qr():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for e in Equipment.query.all():
            png = qr_for_item('equipment', e.equip_id)
            name = f'{e.asset_tag or "EQ-" + str(e.equip_id)}.png'
            zf.writestr(f'equipment/{name}', png)

        for c in Component.query.all():
            png = qr_for_item('component', c.comp_id)
            safe_name = (c.qr_code or f'CP-{c.comp_id}').replace('/', '_')
            zf.writestr(f'components/{safe_name}.png', png)

    buf.seek(0)
    return send_file(
        buf,
        mimetype='application/zip',
        as_attachment=True,
        download_name='lab_qr_codes.zip',
    )


# =========================================================
# GET /api/items/<type>/<id>  — single item detail
# =========================================================
@items_bp.route('/<item_type>/<int:item_id>', methods=['GET'])
def get_item(item_type, item_id):
    if item_type == 'equipment':
        e = Equipment.query.get(item_id)
        if not e:
            return jsonify({'error': 'not found'}), 404
        return jsonify({
            'log_id': None,
            'result_status': 'success',
            'confidence': 1.0,
            'item_type': 'equipment',
            'item_id': e.equip_id,
            'display_name': e.equip_name,
            'lab_name': e.laboratory.lab_name if e.laboratory else None,
            'supplier_name': e.supplier.supplier_name if e.supplier else None,
            'unit_price': float(e.unit_price) if e.unit_price else None,
            'status': e.status,
            'asset_tag': e.asset_tag,
            'serial_no': e.serial_no,
            'qr_code': e.qr_code,
            'quantity': None,
            'low_stock': False,
            'last_txn_date': None,
        }), 200

    if item_type == 'component':
        c = Component.query.get(item_id)
        if not c:
            return jsonify({'error': 'not found'}), 404
        return jsonify({
            'log_id': None,
            'result_status': 'success',
            'confidence': 1.0,
            'item_type': 'component',
            'item_id': c.comp_id,
            'display_name': c.comp_name,
            'lab_name': c.laboratory.lab_name if c.laboratory else None,
            'supplier_name': c.supplier.supplier_name if c.supplier else None,
            'unit_price': float(c.unit_price) if c.unit_price else None,
            'status': None,
            'asset_tag': None,
            'serial_no': None,
            'qr_code': c.qr_code,
            'quantity': c.quantity,
            'unit': c.unit,
            'low_stock': c.low_stock,
            'last_txn_date': None,
        }), 200

    return jsonify({'error': 'invalid item_type'}), 400