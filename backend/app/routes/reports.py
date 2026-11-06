# =========================================================
# app/routes/reports.py
# =========================================================

from flask import Blueprint, send_file
from app.services.report_service import generate_excel_report, generate_pdf_report
from app.utils.security import login_required

reports_bp = Blueprint('reports', __name__)


# =========================================================
# GET /api/reports/inventory.xlsx
# =========================================================
@reports_bp.route('/inventory.xlsx', methods=['GET'])
@login_required
def download_excel():
    buffer = generate_excel_report()
    return send_file(
        buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='JU_Lab_Inventory.xlsx'
    )


# =========================================================
# GET /api/reports/inventory.pdf
# =========================================================
@reports_bp.route('/inventory.pdf', methods=['GET'])
@login_required
def download_pdf():
    buffer = generate_pdf_report()
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name='JU_Lab_Inventory.pdf'
    )