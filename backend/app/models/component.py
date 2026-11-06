# =========================================================
# app/models/component.py
# =========================================================

from datetime import datetime
from app import db


class Component(db.Model):
    __tablename__ = 'components'

    comp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comp_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    unit = db.Column(db.String(20), default='pcs')
    quantity = db.Column(db.Integer, default=0)
    min_threshold = db.Column(db.Integer, default=0)
    unit_price = db.Column(db.Numeric(10, 2))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'))
    lab_id = db.Column(db.Integer, db.ForeignKey('laboratories.lab_id'))
    qr_code = db.Column(db.String(50), unique=True)

    @property
    def low_stock(self):
        return self.quantity <= self.min_threshold

    def to_dict(self):
        return {
            'comp_id': self.comp_id,
            'comp_name': self.comp_name,
            'category': self.category,
            'unit': self.unit,
            'quantity': self.quantity,
            'min_threshold': self.min_threshold,
            'low_stock': self.low_stock,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.supplier_name if self.supplier else None,
            'lab_id': self.lab_id,
            'lab_name': self.laboratory.lab_name if self.laboratory else None,
            'qr_code': self.qr_code,
        }

    def __repr__(self):
        return f'<Component {self.comp_name} qty={self.quantity}>'


class StockTransaction(db.Model):
    __tablename__ = 'stock_transactions'

    txn_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    component_id = db.Column(db.Integer, db.ForeignKey('components.comp_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    txn_type = db.Column(db.Enum('IN', 'OUT', name='stock_txn_type'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    txn_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.String(255))

    # Relationships
    component = db.relationship('Component', backref='transactions')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'txn_id': self.txn_id,
            'component_name': self.component.comp_name if self.component else None,
            'txn_type': self.txn_type,
            'quantity': self.quantity,
            'txn_date': self.txn_date.isoformat(),
            'user_name': self.user.full_name if self.user else None,
            'notes': self.notes
        }