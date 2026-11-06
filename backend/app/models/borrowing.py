from datetime import datetime
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
