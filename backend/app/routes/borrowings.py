# =========================================================
# app/routes/borrowings.py
# POST /api/borrowings               — Borrow an item
# POST /api/borrowings/<id>/return   — Return an item
# GET  /api/borrowings/my            — My active borrowings
# =========================================================

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g

from app import db
from app.models import Equipment, Borrowing
from app.utils.security import login_required

borrowings_bp = Blueprint('borrowings', __name__)


# =========================================================
# POST /api/borrowings
# =========================================================
@borrowings_bp.route('', methods=['POST'])
@login_required
def borrow_item():
    data = request.get_json(silent=True) or {}
    equip_id = data.get('equip_id')
    days = int(data.get('days', 7))  # Default borrow period is 7 days

    if not equip_id:
        return jsonify({'error': 'equip_id required'}), 400

    equip = Equipment.query.get(equip_id)
    if not equip:
        return jsonify({'error': 'Equipment not found'}), 404

    if equip.status != 'available':
        return jsonify({'error': f'Item is currently {equip.status}'}), 400

    # Check if already borrowed by someone
    active_borrow = Borrowing.query.filter_by(
        equip_id=equip_id, status='borrowed'
    ).first()
    if active_borrow:
        return jsonify({'error': 'Item is already borrowed'}), 400

    # Create borrowing record
    borrow_date = datetime.utcnow().date()
    due_date = borrow_date + timedelta(days=days)

    record = Borrowing(
        equip_id=equip_id,
        borrower_id=g.current_user.user_id,
        issued_by=g.current_user.user_id, # For now, user issues to themselves
        borrow_date=borrow_date,
        due_date=due_date,
        status='borrowed'
    )

    # Update equipment status
    equip.status = 'borrowed'

    db.session.add(record)
    db.session.commit()

    return jsonify({
        'message': 'Borrowed successfully',
        'borrow_id': record.borrow_id,
        'due_date': record.due_date.isoformat()
    }), 201


# =========================================================
# POST /api/borrowings/<id>/return
# =========================================================
@borrowings_bp.route('/<int:borrow_id>/return', methods=['POST'])
@login_required
def return_item(borrow_id):
    record = Borrowing.query.get(borrow_id)
    if not record:
        return jsonify({'error': 'Record not found'}), 404

    if record.borrower_id != g.current_user.user_id and g.current_user.role not in ('Admin', 'Storekeeper'):
        return jsonify({'error': 'Not authorized to return this item'}), 403

    if record.status != 'borrowed':
        return jsonify({'error': 'Item already returned'}), 400

    # Update record
    record.return_date = datetime.utcnow().date()
    # Determine if late
    if record.return_date > record.due_date:
        record.status = 'returned_late'
    else:
        record.status = 'returned'
    
    record.condition_on_return = 'good' # Assuming good for now

    # Update equipment status back to available
    equip = Equipment.query.get(record.equip_id)
    if equip:
        equip.status = 'available'

    db.session.commit()

    return jsonify({'message': 'Returned successfully'}), 200


# =========================================================
# GET /api/borrowings/my
# =========================================================
@borrowings_bp.route('/my', methods=['GET'])
@login_required
def my_borrowings():
    # Get active borrowings for this user
    records = Borrowing.query.filter_by(
        borrower_id=g.current_user.user_id,
        status='borrowed'
    ).order_by(Borrowing.due_date.asc()).all()

    results = []
    today = datetime.utcnow().date()
    
    for r in records:
        equip = Equipment.query.get(r.equip_id)
        is_overdue = today > r.due_date
        
        results.append({
            'borrow_id': r.borrow_id,
            'equip_id': r.equip_id,
            'equip_name': equip.equip_name if equip else 'Unknown',
            'asset_tag': equip.asset_tag if equip else '-',
            'due_date': r.due_date.isoformat(),
            'is_overdue': is_overdue,
            'days_left': (r.due_date - today).days if not is_overdue else 0
        })

    return jsonify(results), 200