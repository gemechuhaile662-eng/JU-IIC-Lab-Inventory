# write_models.py — run once from backend/ folder
import os

os.makedirs('app/models', exist_ok=True)

files = {}

# ---------- user.py ----------
files['app/models/user.py'] = '''from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('Admin', 'Technician', 'Storekeeper', 'Viewer', name='user_roles'),
        nullable=False, default='Viewer'
    )
    phone = db.Column(db.String(20))
    status = db.Column(db.Enum('active', 'inactive', name='user_status'), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    borrowings = db.relationship('Borrowing', foreign_keys='Borrowing.borrower_id',
                                 backref='borrower', lazy=True)
    issued_borrowings = db.relationship('Borrowing', foreign_keys='Borrowing.issued_by',
                                        backref='issuer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_sensitive=False):
        data = {
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_sensitive:
            data['password_hash'] = self.password_hash
        return data

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'
'''

# ---------- laboratory.py ----------
files['app/models/laboratory.py'] = '''from app import db


class Laboratory(db.Model):
    __tablename__ = 'laboratories'

    lab_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lab_name = db.Column(db.String(100), nullable=False)
    lab_code = db.Column(db.String(20), unique=True, nullable=False)
    location = db.Column(db.String(100))
    supervisor_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    description = db.Column(db.Text)

    supervisor = db.relationship('User', foreign_keys=[supervisor_id])
    equipment = db.relationship('Equipment', backref='laboratory', lazy=True)
    components = db.relationship('Component', backref='laboratory', lazy=True)

    def to_dict(self):
        return {
            'lab_id': self.lab_id,
            'lab_name': self.lab_name,
            'lab_code': self.lab_code,
            'location': self.location,
            'supervisor_id': self.supervisor_id,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Laboratory {self.lab_code}>'
'''

# ---------- supplier.py ----------
files['app/models/supplier.py'] = '''from app import db


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))

    equipment = db.relationship('Equipment', backref='supplier', lazy=True)
    components = db.relationship('Component', backref='supplier', lazy=True)

    def to_dict(self):
        return {
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
        }

    def __repr__(self):
        return f'<Supplier {self.supplier_name}>'
'''

# ---------- equipment.py ----------
files['app/models/equipment.py'] = '''from datetime import datetime
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
'''

# ---------- component.py ----------
files['app/models/component.py'] = '''from app import db


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
'''

# ---------- borrowing.py ----------
files['app/models/borrowing.py'] = '''from datetime import datetime
from app import db


class Borrowing(db.Model):
    __tablename__ = 'borrowings'

    borrow_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equip_id = db.Column(db.Integer, db.ForeignKey('equipment.equip_id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=lambda: datetime.utcnow().date())
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(
        db.Enum('borrowed', 'returned', 'returned_late', 'overdue', 'lost',
                name='borrow_status'),
        default='borrowed'
    )
    condition_on_return = db.Column(db.String(50))

    def to_dict(self):
        return {
            'borrow_id': self.borrow_id,
            'equip_id': self.equip_id,
            'equip_name': self.equipment.equip_name if self.equipment else None,
            'asset_tag': self.equipment.asset_tag if self.equipment else None,
            'borrower_id': self.borrower_id,
            'borrower_name': self.borrower.full_name if self.borrower else None,
            'issued_by': self.issued_by,
            'issuer_name': self.issuer.full_name if self.issuer else None,
            'borrow_date': self.borrow_date.isoformat() if self.borrow_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'condition_on_return': self.condition_on_return,
        }

    def __repr__(self):
        return f'<Borrowing {self.borrow_id} equip={self.equip_id}>'
'''

# ---------- maintenance.py ----------
files['app/models/maintenance.py'] = '''from app import db


class Maintenance(db.Model):
    __tablename__ = 'maintenance'

    maint_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equip_id = db.Column(db.Integer, db.ForeignKey('equipment.equip_id'), nullable=False)
    maint_type = db.Column(
        db.Enum('repair', 'calibration', 'service', name='maint_type'),
        nullable=False
    )
    reported_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    technician_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    cost = db.Column(db.Numeric(10, 2), default=0)
    status = db.Column(
        db.Enum('pending', 'in_progress', 'completed', 'cancelled',
                name='maint_status'),
        default='pending'
    )
    description = db.Column(db.Text)

    reporter = db.relationship('User', foreign_keys=[reported_by])
    technician = db.relationship('User', foreign_keys=[technician_id])

    def to_dict(self):
        return {
            'maint_id': self.maint_id,
            'equip_id': self.equip_id,
            'equip_name': self.equipment.equip_name if self.equipment else None,
            'maint_type': self.maint_type,
            'reported_by': self.reported_by,
            'reporter_name': self.reporter.full_name if self.reporter else None,
            'technician_id': self.technician_id,
            'technician_name': self.technician.full_name if self.technician else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'cost': float(self.cost) if self.cost else 0,
            'status': self.status,
            'description': self.description,
        }

    def __repr__(self):
        return f'<Maintenance {self.maint_id} ({self.maint_type})>'
'''

# ---------- recognition.py ----------
files['app/models/recognition.py'] = '''from datetime import datetime
from app import db


class ItemClass(db.Model):
    __tablename__ = 'item_classes'

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), unique=True, nullable=False)
    item_type = db.Column(db.Enum('equipment', 'component', name='item_type'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    confidence_threshold = db.Column(db.Float, default=0.75)
    display_name = db.Column(db.String(100))

    def to_dict(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'confidence_threshold': self.confidence_threshold,
            'display_name': self.display_name,
        }

    def __repr__(self):
        return f'<ItemClass {self.class_name} -> {self.item_type}#{self.item_id}>'


class RecognitionLog(db.Model):
    __tablename__ = 'recognition_logs'

    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    image_path = db.Column(db.String(255))
    detected_class_id = db.Column(db.Integer, db.ForeignKey('item_classes.class_id'))
    confidence = db.Column(db.Float)
    item_type = db.Column(db.String(20))
    item_id = db.Column(db.Integer)
    result_status = db.Column(
        db.Enum('success', 'low_confidence', 'unknown_item', 'qr_fallback',
                'user_corrected', name='recognition_status'),
        default='success'
    )
    photo_date = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
    detected_class = db.relationship('ItemClass')

    def to_dict(self):
        return {
            'log_id': self.log_id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'detected_class_id': self.detected_class_id,
            'confidence': self.confidence,
            'item_type': self.item_type,
            'item_id': self.item_id,
            'result_status': self.result_status,
            'photo_date': self.photo_date.isoformat() if self.photo_date else None,
        }


class RecognitionCorrection(db.Model):
    __tablename__ = 'recognition_corrections'

    correction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_id = db.Column(db.Integer, db.ForeignKey('recognition_logs.log_id'), nullable=False)
    predicted_class_id = db.Column(db.Integer, db.ForeignKey('item_classes.class_id'))
    correct_class_id = db.Column(db.Integer, db.ForeignKey('item_classes.class_id'))
    corrected_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    corrected_at = db.Column(db.DateTime, default=datetime.utcnow)

    log = db.relationship('RecognitionLog')
    predicted_class = db.relationship('ItemClass', foreign_keys=[predicted_class_id])
    correct_class = db.relationship('ItemClass', foreign_keys=[correct_class_id])
    user = db.relationship('User')

    def to_dict(self):
        return {
            'correction_id': self.correction_id,
            'log_id': self.log_id,
            'predicted_class_id': self.predicted_class_id,
            'correct_class_id': self.correct_class_id,
            'corrected_by': self.corrected_by,
            'corrected_at': self.corrected_at.isoformat() if self.corrected_at else None,
        }
'''

# ---------- __init__.py ----------
files['app/models/__init__.py'] = '''from app.models.user import User
from app.models.laboratory import Laboratory
from app.models.supplier import Supplier
from app.models.equipment import Equipment
from app.models.component import Component
from app.models.borrowing import Borrowing
from app.models.maintenance import Maintenance
from app.models.recognition import (
    ItemClass,
    RecognitionLog,
    RecognitionCorrection,
)

__all__ = [
    'User',
    'Laboratory',
    'Supplier',
    'Equipment',
    'Component',
    'Borrowing',
    'Maintenance',
    'ItemClass',
    'RecognitionLog',
    'RecognitionCorrection',
]
'''

for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'✅ wrote {path}')

print('\n🎉 All 9 model files written correctly.')
print('Next: del data\\inventory.db, then python run.py')