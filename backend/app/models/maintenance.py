from app import db


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
