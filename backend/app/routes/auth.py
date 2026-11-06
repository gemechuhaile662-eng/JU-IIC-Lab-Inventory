# =========================================================
# app/routes/auth.py
# POST /api/auth/register
# POST /api/auth/login
# POST /api/auth/logout
# GET  /api/auth/me
# GET  /api/auth/users
# PUT  /api/auth/users/<id>/role
# PUT  /api/auth/users/<id>/reset-password
# POST /api/auth/forgot-password
# POST /api/auth/reset-password
# =========================================================

import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, session, g, current_app
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, PasswordResetToken
from app.utils.security import login_required, role_required, current_user

auth_bp = Blueprint('auth', __name__)


# =========================================================
# POST /api/auth/register
# =========================================================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    full_name = (data.get('full_name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    phone = data.get('phone')

    # Force everyone to Viewer upon registration
    role = 'Viewer'

    # Validate
    if not full_name or not email or not password:
        return jsonify({'error': 'full_name, email, password required'}), 400
    if len(password) < 6:
        return jsonify({'error': 'password must be at least 6 chars'}), 400

    # Check duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already registered'}), 409

    user = User(
        full_name=full_name,
        email=email,
        role=role,
        phone=phone,
        status='active'
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'could not create user'}), 500

    # Auto-login after register
    session['user_id'] = user.user_id

    return jsonify({
        'message': 'registered',
        'user': user.to_dict()
    }), 201


# =========================================================
# POST /api/auth/login
# =========================================================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401

    if user.status != 'active':
        return jsonify({'error': 'account is inactive'}), 403

    session['user_id'] = user.user_id

    return jsonify({
        'message': 'logged in',
        'user': user.to_dict()
    }), 200


# =========================================================
# POST /api/auth/logout
# =========================================================
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'logged out'}), 200


# =========================================================
# GET /api/auth/me
# =========================================================
@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    return jsonify(current_user().to_dict()), 200


# =========================================================
# GET /api/auth/users  (Admin only)
# =========================================================
@auth_bp.route('/users', methods=['GET'])
@role_required('Admin')
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


# =========================================================
# PUT /api/auth/users/<id>/role  (Admin only)
# =========================================================
@auth_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@role_required('Admin')
def update_user_role(user_id):
    data = request.get_json(silent=True) or {}
    new_role = data.get('role')

    if new_role not in ('Admin', 'Technician', 'Storekeeper', 'Viewer'):
        return jsonify({'error': 'Invalid role'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prevent admin from changing their own role
    if user.user_id == g.current_user.user_id:
        return jsonify({'error': 'You cannot change your own role'}), 400

    user.role = new_role
    db.session.commit()

    return jsonify({'message': 'Role updated successfully', 'user': user.to_dict()}), 200


# =========================================================
# PUT /api/auth/users/<id>/reset-password  (Admin only)
# =========================================================
@auth_bp.route('/users/<int:user_id>/reset-password', methods=['PUT'])
@role_required('Admin')
def reset_user_password(user_id):
    data = request.get_json(silent=True) or {}
    new_password = data.get('password')

    if not new_password or len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password reset successfully'}), 200


# =========================================================
# POST /api/auth/forgot-password
# =========================================================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get('email') or '').strip().lower()

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'If that email exists, a reset link has been sent.'}), 200

    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)

    reset_record = PasswordResetToken(user_id=user.user_id, token=token, expires_at=expires)
    db.session.add(reset_record)
    db.session.commit()

    reset_link = f"{current_app.config['FRONTEND_URL']}/reset-password.html?token={token}"

    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_EMAIL']
        msg['To'] = user.email
        msg['Subject'] = "JU-IIC Lab Inventory - Password Reset"

        body = f"Hello {user.full_name},\n\nClick the link below to reset your password. It expires in 1 hour.\n\n{reset_link}\n\nIf you did not request this, ignore this email."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(current_app.config['MAIL_EMAIL'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        
        return jsonify({'message': 'Email sent successfully'}), 200
    except Exception as e:
        print(f"EMAIL ERROR: {e}")
        return jsonify({'error': 'Failed to send email. Check server logs.'}), 500


# =========================================================
# POST /api/auth/reset-password
# =========================================================
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password_with_token():
    data = request.get_json(silent=True) or {}
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password or len(new_password) < 6:
        return jsonify({'error': 'Valid token and password (min 6 chars) required'}), 400

    reset_record = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_record:
        return jsonify({'error': 'Invalid or expired token'}), 400
        
    if datetime.utcnow() > reset_record.expires_at:
        db.session.delete(reset_record)
        db.session.commit()
        return jsonify({'error': 'Token has expired. Please request a new one.'}), 400

    user = User.query.get(reset_record.user_id)
    user.set_password(new_password)

    db.session.delete(reset_record)
    db.session.commit()

    return jsonify({'message': 'Password reset successfully. You can now login.'}), 200