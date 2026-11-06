# =========================================================
# app/services/report_service.py
# Generates PDF and Excel reports
# =========================================================

import io
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from app.models import Equipment, Component


# =========================================================
# EXCEL REPORT
# =========================================================
def generate_excel_report():
    """Generate an Excel file of all equipment and components."""
    wb = Workbook()
    
    # --- Styles ---
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2563EB", end_color="2563EB", fill_type="solid")
    align_center = Alignment(horizontal="center")

    # =========================================================
    # Sheet 1: Equipment
    # =========================================================
    ws1 = wb.active
    ws1.title = "Equipment"
    
    headers1 = ["Asset Tag", "Name", "Category", "Lab", "Supplier", "Serial No", "Status", "Price (ETB)"]
    ws1.append(headers1)

    for col_num, _ in enumerate(headers1, 1):
        cell = ws1.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center

    for eq in Equipment.query.all():
        ws1.append([
            eq.asset_tag,
            eq.equip_name,
            eq.category or '-',
            eq.laboratory.lab_name if eq.laboratory else '-',
            eq.supplier.supplier_name if eq.supplier else '-',
            eq.serial_no or '-',
            eq.status.replace('_', ' ').title(),
            float(eq.unit_price) if eq.unit_price else 0
        ])

    # =========================================================
    # Sheet 2: Components
    # =========================================================
    ws2 = wb.create_sheet(title="Components")
    
    headers2 = ["QR Code", "Name", "Category", "Lab", "Quantity", "Unit", "Low Stock?", "Price (ETB)"]
    ws2.append(headers2)

    for col_num, _ in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center

    for cp in Component.query.all():
        ws2.append([
            cp.qr_code or '-',
            cp.comp_name,
            cp.category or '-',
            cp.laboratory.lab_name if cp.laboratory else '-',
            cp.quantity,
            cp.unit or 'pcs',
            "YES" if cp.low_stock else "No",
            float(cp.unit_price) if cp.unit_price else 0
        ])

    # Auto-adjust column widths
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_length = 0
            column = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = min(adjusted_width, 40)

    # Save to memory buffer
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


# =========================================================
# PDF REPORT
# =========================================================
def generate_pdf_report():
    """Generate a PDF file of all equipment and components."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(A4),
        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
    )
    
    elements = []
    styles = getSampleStyleSheet()

    # --- Title ---
    title = Paragraph("<b>JU-IIC Lab Inventory Report</b>", styles['Title'])
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    subtitle = Paragraph(f"Generated on: {date_str}", styles['Normal'])
    
    elements.append(title)
    elements.append(subtitle)
    elements.append(Spacer(1, 20))

    # =========================================================
    # Equipment Table
    # =========================================================
    elements.append(Paragraph("<b>1. Equipment</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    eq_data = [["Asset Tag", "Name", "Lab", "Status", "Price (ETB)"]]
    for eq in Equipment.query.all():
        eq_data.append([
            eq.asset_tag,
            Paragraph(eq.equip_name, styles['Normal']),
            Paragraph(eq.laboratory.lab_name if eq.laboratory else '-', styles['Normal']),
            eq.status.replace('_', ' ').title(),
            f"{float(eq.unit_price):,.2f}" if eq.unit_price else "0.00"
        ])

    eq_table = Table(eq_data, colWidths=[80, 200, 150, 100, 80])
    eq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(eq_table)
    elements.append(Spacer(1, 30))

    # =========================================================
    # Components Table
    # =========================================================
    elements.append(Paragraph("<b>2. Components</b>", styles['Heading2']))
    elements.append(Spacer(1, 10))

    cp_data = [["QR Code", "Name", "Lab", "Qty", "Low Stock", "Price (ETB)"]]
    for cp in Component.query.all():
        cp_data.append([
            cp.qr_code or '-',
            Paragraph(cp.comp_name, styles['Normal']),
            Paragraph(cp.laboratory.lab_name if cp.laboratory else '-', styles['Normal']),
            str(cp.quantity),
            "YES" if cp.low_stock else "No",
            f"{float(cp.unit_price):,.2f}" if cp.unit_price else "0.00"
        ])

    cp_table = Table(cp_data, colWidths=[80, 200, 150, 60, 80, 80])
    cp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2563EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(cp_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer