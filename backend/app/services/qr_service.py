# =========================================================
# app/services/qr_service.py
# QR code generation helpers
# =========================================================

import os
import io
import qrcode
from qrcode.image.pil import PilImage

from flask import current_app


def generate_qr_bytes(data: str, box_size: int = 10, border: int = 2) -> bytes:
    """Generate a QR code image (PNG bytes) for the given data string."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def qr_for_item(item_type: str, item_id: int) -> bytes:
    """
    Generate QR for a specific item. The QR payload is a URL that
    the frontend can decode and route to result.html.
    """
    payload = f'{item_type}:{item_id}'
    return generate_qr_bytes(payload)


def qr_for_qr_code(qr_code_string: str) -> bytes:
    """Generate QR for an existing QR code string (e.g., 'QR-EQ-0001')."""
    return generate_qr_bytes(qr_code_string)