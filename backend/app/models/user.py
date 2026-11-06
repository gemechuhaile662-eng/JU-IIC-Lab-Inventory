from datetime import datetime
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
class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User')