from datetime import datetime
from app import db


class Equipment(db.Model):
    __tablename__ = 'equipment'

    equip_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asset_tag = db.Column(db.String(20), unique=True, nullable=False, index=True)
    equip_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    lab_id = db.Column(db.Integer, db.ForeignKey('laboratories.lab_id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'))
    serial_no = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    unit_price = db.Column(db.Numeric(12, 2))
    status = db.Column(
        db.Enum('available', 'borrowed', 'damaged', 'under_maintenance', 'retired',
                name='equipment_status'),
        default='available'
    )
    qr_code = db.Column(db.String(50), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrowings = db.relationship('Borrowing', backref='equipment', lazy=True)
    maintenance_records = db.relationship('Maintenance', backref='equipment', lazy=True)

    def to_dict(self):
        return {
            'equip_id': self.equip_id,
            'asset_tag': self.asset_tag,
            'equip_name': self.equip_name,
            'category': self.category,
            'lab_id': self.lab_id,
            'lab_name': self.laboratory.lab_name if self.laboratory else None,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.supplier_name if self.supplier else None,
            'serial_no': self.serial_no,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'status': self.status,
            'qr_code': self.qr_code,
        }

    def __repr__(self):
        return f'<Equipment {self.asset_tag}>'
