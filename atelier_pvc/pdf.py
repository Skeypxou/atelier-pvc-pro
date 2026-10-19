"""Génération PDF des devis et factures."""

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape


def document_pdf(title: str, document: dict, client: dict | None = None, kind: str = "devis") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"{title} {document.get('number', '')}",
    )
    styles = getSampleStyleSheet()
    story = [Paragraph("Atelier PVC Pro", styles["Title"]), Paragraph(title, styles["Heading1"]), Spacer(1, 5 * mm)]
    story.append(Paragraph(f"<b>Numéro :</b> {escape(str(document.get('number', '-')))}", styles["Normal"]))
    story.append(Paragraph(f"<b>Date :</b> {document.get('date', '-')}", styles["Normal"]))
    if client:
        story.append(Paragraph(f"<b>Client :</b> {escape(str(client.get('name', '-')))}", styles["Normal"]))
        if client.get("phone"):
            story.append(Paragraph(f"<b>Téléphone :</b> {escape(str(client.get('phone')))}", styles["Normal"]))
        if client.get("address"):
            story.append(Paragraph(f"<b>Adresse :</b> {escape(str(client.get('address')))}", styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    rows = [["Désignation", "Qté", "Prix unitaire", "Total"]]
    for line in document.get("lines", []):
        rows.append([
            escape(str(line.get("description", ""))),
            str(line.get("quantity", 0)),
            f"{float(line.get('unit_price', 0)):.2f} DA",
            f"{float(line.get('line_total', 0)):.2f} DA",
        ])
    if len(rows) == 1:
        rows.append([str(document.get("description", kind.title())), "1", f"{float(document.get('total', 0)):.2f} DA", f"{float(document.get('total', 0)):.2f} DA"])
    table = Table(rows, colWidths=[83 * mm, 17 * mm, 33 * mm, 35 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17324D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D7DE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(table)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(f"<b>Sous-total :</b> {float(document.get('subtotal', document.get('total', 0))):.2f} DA", styles["Normal"]))
    story.append(Paragraph(f"<b>TVA :</b> {float(document.get('tax', 0)):.2f} DA", styles["Normal"]))
    story.append(Paragraph(f"<b>TOTAL :</b> {float(document.get('total', 0)):.2f} DA", styles["Heading2"]))
    if document.get("notes"):
        story.extend([Spacer(1, 5 * mm), Paragraph(f"<b>Notes :</b> {escape(str(document['notes']))}", styles["Normal"])])
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Document généré par Atelier PVC Pro.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()
