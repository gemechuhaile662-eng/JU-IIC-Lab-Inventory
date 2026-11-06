from app import db


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
