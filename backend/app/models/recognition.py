from datetime import datetime
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
