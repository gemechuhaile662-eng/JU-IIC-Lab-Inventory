# =========================================================
# app/routes/stock.py
# POST /api/stock/in         — Add stock
# POST /api/stock/out        — Remove stock
# GET  /api/stock/recent     — Recent stock movements
# =========================================================

from flask import Blueprint, request, jsonify, g
from app import db
from app.models import Component, StockTransaction
from app.utils.security import role_required

stock_bp = Blueprint('stock', __name__)

# =========================================================
# POST /api/stock/in
# =========================================================
@stock_bp.route('/in', methods=['POST'])
@role_required('Admin', 'Storekeeper', 'Technician')
def stock_in():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('component_id')
    qty = int(data.get('quantity', 0))
    notes = data.get('notes', 'Stock In')

    if qty <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400

    comp = Component.query.get(comp_id)
    if not comp:
        return jsonify({'error': 'Component not found'}), 404

    # Update component quantity
    comp.quantity += qty

    # Log transaction
    txn = StockTransaction(
        component_id=comp_id,
        user_id=g.current_user.user_id,
        txn_type='IN',
        quantity=qty,
        notes=notes
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({'message': 'Stock added', 'new_quantity': comp.quantity}), 200


# =========================================================
# POST /api/stock/out
# =========================================================
@stock_bp.route('/out', methods=['POST'])
@role_required('Admin', 'Storekeeper', 'Technician')
def stock_out():
    data = request.get_json(silent=True) or {}
    comp_id = data.get('component_id')
    qty = int(data.get('quantity', 0))
    notes = data.get('notes', 'Stock Out')

    if qty <= 0:
        return jsonify({'error': 'Quantity must be greater than 0'}), 400

    comp = Component.query.get(comp_id)
    if not comp:
        return jsonify({'error': 'Component not found'}), 404

    if comp.quantity < qty:
        return jsonify({'error': f'Not enough stock. Only {comp.quantity} left.'}), 400

    # Update component quantity
    comp.quantity -= qty

    # Log transaction
    txn = StockTransaction(
        component_id=comp_id,
        user_id=g.current_user.user_id,
        txn_type='OUT',
        quantity=qty,
        notes=notes
    )
    db.session.add(txn)
    db.session.commit()

    return jsonify({'message': 'Stock removed', 'new_quantity': comp.quantity}), 200


# =========================================================
# GET /api/stock/recent
# =========================================================
@stock_bp.route('/recent', methods=['GET'])
@role_required('Admin', 'Storekeeper', 'Technician', 'Viewer')
def recent_stock():
    # Get last 20 transactions
    txns = StockTransaction.query.order_by(StockTransaction.txn_date.desc()).limit(20).all()

    results = []
    for t in txns:
        results.append({
            'txn_id': t.txn_id,
            'component_name': t.component.comp_name if t.component else 'Unknown',
            'txn_type': t.txn_type,
            'quantity': t.quantity,
            'user_name': t.user.full_name if t.user else 'System',
            'txn_date': t.txn_date.isoformat(),
            'notes': t.notes
        })

    return jsonify(results), 200