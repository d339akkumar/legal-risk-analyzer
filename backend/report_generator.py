import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ── Colours ───────────────────────────────────────────────────────────────────
C_NAVY       = colors.HexColor("#1a1d3a")
C_NAVY_LIGHT = colors.HexColor("#252850")
C_ACCENT     = colors.HexColor("#4a6cf7")
C_ACCENT2    = colors.HexColor("#e8edff")
C_HIGH       = colors.HexColor("#c0392b")
C_HIGH_LIGHT = colors.HexColor("#fdecea")
C_MED        = colors.HexColor("#d68910")
C_MED_LIGHT  = colors.HexColor("#fef9e7")
C_LOW        = colors.HexColor("#1e8449")
C_LOW_LIGHT  = colors.HexColor("#eafaf1")
C_TEXT       = colors.HexColor("#1c1c2e")
C_TEXT2      = colors.HexColor("#4a4a6a")
C_MUTED      = colors.HexColor("#8888aa")
C_BORDER     = colors.HexColor("#dde0f0")
C_BG_LIGHT   = colors.HexColor("#f7f8fc")
C_WHITE      = colors.white
C_TRACK      = colors.HexColor("#e0e4f5")


def _risk_color(risk):
    return {"High": C_HIGH, "Medium": C_MED, "Low": C_LOW}.get(risk, C_MUTED)

def _risk_light(risk):
    return {"High": C_HIGH_LIGHT, "Medium": C_MED_LIGHT, "Low": C_LOW_LIGHT}.get(risk, C_BG_LIGHT)

def _risk_label_color(risk):
    # darker shade for text on light background
    return {"High": colors.HexColor("#922b21"),
            "Medium": colors.HexColor("#9a6006"),
            "Low":  colors.HexColor("#145a32")}.get(risk, C_MUTED)


def _md_to_rl(text: str) -> str:
    """Convert basic markdown bold/italic to ReportLab XML tags."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)
    # Replace plain newlines with <br/>
    text = text.replace('\n', '<br/>')
    return text


def _styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "title": s("RTitle",
            fontSize=22, fontName="Helvetica-Bold",
            textColor=C_WHITE, alignment=TA_LEFT, leading=26),

        "header_date": s("RHDate",
            fontSize=8.5, fontName="Helvetica",
            textColor=colors.HexColor("#aab0d0"), alignment=TA_RIGHT),

        "header_sub": s("RHSub",
            fontSize=9, fontName="Helvetica",
            textColor=colors.HexColor("#8890c0"), alignment=TA_LEFT),

        "section": s("RSection",
            fontSize=10, fontName="Helvetica-Bold",
            textColor=C_ACCENT, spaceBefore=4, spaceAfter=4,
            letterSpacing=0.8),

        "body": s("RBody",
            fontSize=9, fontName="Helvetica",
            textColor=C_TEXT, spaceAfter=4, leading=14),

        "ai": s("RAI",
            fontSize=9.5, fontName="Helvetica",
            textColor=C_TEXT, leading=16, spaceAfter=4),

        "clause": s("RClause",
            fontSize=8.5, fontName="Helvetica",
            textColor=C_TEXT2, leading=13, spaceAfter=3),

        "expl": s("RExpl",
            fontSize=8, fontName="Helvetica-Oblique",
            textColor=C_MUTED, leading=11, spaceAfter=0),

        "meta": s("RMeta",
            fontSize=8, fontName="Helvetica",
            textColor=C_MUTED, alignment=TA_RIGHT),

        "centered": s("RCentered",
            fontSize=8, fontName="Helvetica",
            textColor=C_MUTED, alignment=TA_CENTER),

        "score_num": s("RScoreNum",
            fontSize=38, fontName="Helvetica-Bold",
            textColor=C_TEXT, alignment=TA_CENTER, leading=42),

        "metric_num": s("RMetNum",
            fontSize=26, fontName="Helvetica-Bold",
            textColor=C_TEXT, alignment=TA_CENTER, leading=30),

        "footer": s("RFooter",
            fontSize=7, fontName="Helvetica-Oblique",
            textColor=C_MUTED, alignment=TA_CENTER, leading=10),

        "page_num": s("RPageNum",
            fontSize=7.5, fontName="Helvetica",
            textColor=C_MUTED, alignment=TA_RIGHT),
    }


def generate_report(
    results: list,
    score: float,
    level: str,
    high_count: int,
    ai_summary: str,
    fraud_alerts: list,
    output_dir: str = None       # None = in-memory only (for deployment)
) -> tuple:
    """
    Generate PDF report.
    Returns (pdf_bytes, filename) always.
    If output_dir is provided AND we are running locally, also saves to disk.
    """
    import io

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"contract_risk_report_{timestamp}.pdf"

    # Always build into memory buffer first
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=2*cm,
    )

    ST    = _styles()
    W     = A4[0] - 4*cm
    story = []

    high_r = [r for r in results if r["risk"] == "High"]
    med_r  = [r for r in results if r["risk"] == "Medium"]
    low_r  = [r for r in results if r["risk"] == "Low"]
    level_color = C_HIGH if "High" in level else C_MED if "Medium" in level else C_LOW
    level_light = _risk_light(level.split()[0] if level else "Low")

    # ── PAGE 1: HEADER ────────────────────────────────────────────────────────
    header_data = [[
        [
            Paragraph("CONTRACT RISK REPORT", ST["title"]),
            Spacer(1, 4),
            Paragraph("Legal Risk Analyzer  |  BERT Classifier + AI Counsel", ST["header_sub"]),
        ],
        [
            Paragraph(
                f"Generated<br/>{datetime.now().strftime('%d %B %Y')}<br/>"
                f"{datetime.now().strftime('%I:%M %p')}",
                ST["header_date"]
            )
        ]
    ]]
    header_tbl = Table(header_data, colWidths=[W * 0.68, W * 0.32])
    header_tbl.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), C_NAVY),
        ("TOPPADDING",   (0,0), (-1,-1), 18),
        ("BOTTOMPADDING",(0,0), (-1,-1), 18),
        ("LEFTPADDING",  (0,0), (-1,-1), 18),
        ("RIGHTPADDING", (0,0), (-1,-1), 14),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",    (0,0), (-1,-1), 3, C_ACCENT),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 18))

    # ── SCORE CARD ────────────────────────────────────────────────────────────
    def metric_cell(value, label, color):
        return [
            Paragraph(str(value), ParagraphStyle(f"mv_{label}",
                fontSize=28, fontName="Helvetica-Bold",
                textColor=color, alignment=TA_CENTER, leading=32)),
            Paragraph(label, ST["centered"]),
        ]

    score_data = [[
        [   # score cell
            Paragraph(f"{score:.2f}", ST["score_num"]),
            Paragraph("out of 3.00", ST["centered"]),
        ],
        [   # level cell
            Paragraph(level, ParagraphStyle("lvl",
                fontSize=13, fontName="Helvetica-Bold",
                textColor=level_color, alignment=TA_CENTER, leading=16)),
            Paragraph("risk level", ST["centered"]),
        ],
        metric_cell(len(high_r), "high risk",    C_HIGH),
        metric_cell(len(med_r),  "medium risk",  C_MED),
        metric_cell(len(low_r),  "low risk",     C_LOW),
    ]]

    score_tbl = Table(score_data, colWidths=[W*0.22, W*0.2, W*0.19, W*0.19, W*0.2])
    score_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_WHITE),
        ("BACKGROUND",    (0,0), (0,-1),  C_BG_LIGHT),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 0.8, C_BORDER),
        ("LINEBEFORE",    (1,0), (4,-1),  0.5, C_BORDER),
        ("LINEBELOW",     (0,0), (-1,0),  0.5, C_BORDER),
        # left accent bar
        ("LINEBEFORE",    (0,0), (0,-1),  4,   level_color),
    ]))
    story.append(score_tbl)
    story.append(Spacer(1, 8))

    # ── RISK BAR (track + fill) ───────────────────────────────────────────────
    fill_w   = max(W * (score / 3.0), 0.5*cm)
    track_w  = W - fill_w

    bar_rows = [[
        "",   # fill segment
        "",   # remaining track
    ]]
    bar_tbl = Table(bar_rows, colWidths=[fill_w, track_w], rowHeights=[8])
    bar_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (0,-1), level_color),
        ("BACKGROUND",    (1,0), (1,-1), C_TRACK),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))
    story.append(bar_tbl)

    # bar labels
    bar_labels = Table([[
        Paragraph("Low", ST["centered"]),
        Paragraph("Medium", ST["centered"]),
        Paragraph("High", ST["centered"]),
    ]], colWidths=[W/3]*3)
    bar_labels.setStyle(TableStyle([("ALIGN",(0,0),(-1,-1),"CENTER")]))
    story.append(Spacer(1, 3))
    story.append(bar_labels)
    story.append(Spacer(1, 18))

    # ── AI COUNSEL SUMMARY ────────────────────────────────────────────────────
    story.append(Paragraph("AI COUNSEL SUMMARY", ST["section"]))
    story.append(HRFlowable(width=W, thickness=0.8, color=C_ACCENT, spaceAfter=8))

    # Clean the summary — convert markdown bold to ReportLab XML
    clean_summary = _md_to_rl(ai_summary)

    ai_data = [[Paragraph(clean_summary, ST["ai"])]]
    ai_tbl  = Table(ai_data, colWidths=[W])
    ai_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_ACCENT2),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
        ("BOX",           (0,0), (-1,-1), 0.5, C_ACCENT),
        ("LINEBEFORE",    (0,0), (0,-1),  4,   C_ACCENT),
    ]))
    story.append(ai_tbl)
    story.append(Spacer(1, 18))

    # ── RISK SUMMARY TABLE ────────────────────────────────────────────────────
    story.append(Paragraph("RISK BREAKDOWN", ST["section"]))
    story.append(HRFlowable(width=W, thickness=0.8, color=C_ACCENT, spaceAfter=8))

    breakdown_header = [
        Paragraph("Risk Level", ParagraphStyle("bh", fontSize=8.5,
            fontName="Helvetica-Bold", textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Clauses", ParagraphStyle("bh2", fontSize=8.5,
            fontName="Helvetica-Bold", textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Share", ParagraphStyle("bh3", fontSize=8.5,
            fontName="Helvetica-Bold", textColor=C_WHITE, alignment=TA_CENTER)),
        Paragraph("Avg. Confidence", ParagraphStyle("bh4", fontSize=8.5,
            fontName="Helvetica-Bold", textColor=C_WHITE, alignment=TA_CENTER)),
    ]
    total = len(results)

    def avg_conf(group):
        if not group: return 0
        return sum(r["confidence"] for r in group) / len(group)

    breakdown_rows = [breakdown_header]
    for label, group, color, lcolor in [
        ("High Risk",   high_r, C_HIGH_LIGHT, C_HIGH),
        ("Medium Risk", med_r,  C_MED_LIGHT,  C_MED),
        ("Low Risk",    low_r,  C_LOW_LIGHT,  C_LOW),
    ]:
        pct  = f"{len(group)/total*100:.1f}%" if total else "0%"
        conf = f"{avg_conf(group)*100:.1f}%"
        breakdown_rows.append([
            Paragraph(label, ParagraphStyle(f"bl_{label}", fontSize=8.5,
                fontName="Helvetica-Bold", textColor=lcolor, alignment=TA_CENTER)),
            Paragraph(str(len(group)), ParagraphStyle(f"bv_{label}", fontSize=8.5,
                fontName="Helvetica", textColor=C_TEXT, alignment=TA_CENTER)),
            Paragraph(pct, ParagraphStyle(f"bp_{label}", fontSize=8.5,
                fontName="Helvetica", textColor=C_TEXT, alignment=TA_CENTER)),
            Paragraph(conf, ParagraphStyle(f"bc_{label}", fontSize=8.5,
                fontName="Helvetica", textColor=C_TEXT, alignment=TA_CENTER)),
        ])

    breakdown_tbl = Table(breakdown_rows, colWidths=[W*0.28, W*0.2, W*0.2, W*0.32])
    breakdown_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  C_NAVY),
        ("BACKGROUND",    (0,1), (-1,1),  C_HIGH_LIGHT),
        ("BACKGROUND",    (0,2), (-1,2),  C_MED_LIGHT),
        ("BACKGROUND",    (0,3), (-1,3),  C_LOW_LIGHT),
        ("TOPPADDING",    (0,0), (-1,-1), 9),
        ("BOTTOMPADDING", (0,0), (-1,-1), 9),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("BOX",           (0,0), (-1,-1), 0.8, C_BORDER),
        ("INNERGRID",     (0,0), (-1,-1), 0.3, C_BORDER),
        ("LINEBEFORE",    (0,1), (0,1),   4,   C_HIGH),
        ("LINEBEFORE",    (0,2), (0,2),   4,   C_MED),
        ("LINEBEFORE",    (0,3), (0,3),   4,   C_LOW),
    ]))
    story.append(breakdown_tbl)
    story.append(Spacer(1, 18))

    # ── FRAUD FLAGS ───────────────────────────────────────────────────────────
    if fraud_alerts:
        story.append(Paragraph("FRAUD & ANOMALY FLAGS", ST["section"]))
        story.append(HRFlowable(width=W, thickness=0.8, color=C_HIGH, spaceAfter=8))
        for i, alert in enumerate(fraud_alerts, 1):
            alert_data = [[
                Paragraph(f"!", ParagraphStyle("ai",
                    fontSize=11, fontName="Helvetica-Bold",
                    textColor=C_HIGH, alignment=TA_CENTER)),
                Paragraph(f"<b>Flag {i}:</b> {alert}", ParagraphStyle("at",
                    fontSize=8.5, fontName="Helvetica",
                    textColor=colors.HexColor("#7b241c"), leading=13)),
            ]]
            alert_tbl = Table(alert_data, colWidths=[0.7*cm, W - 0.9*cm])
            alert_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), C_HIGH_LIGHT),
                ("BACKGROUND",    (0,0), (0,-1),  colors.HexColor("#f5b7b1")),
                ("TOPPADDING",    (0,0), (-1,-1), 8),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                ("LEFTPADDING",   (0,0), (0,-1),  6),
                ("LEFTPADDING",   (1,0), (1,-1),  10),
                ("RIGHTPADDING",  (0,0), (-1,-1), 10),
                ("BOX",           (0,0), (-1,-1), 0.5, colors.HexColor("#e74c3c")),
                ("LINEBEFORE",    (0,0), (0,-1),  3,   C_HIGH),
                ("ALIGN",         (0,0), (0,-1),  "CENTER"),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(alert_tbl)
            story.append(Spacer(1, 5))
        story.append(Spacer(1, 10))

    # ── PAGE 2: CLAUSE BY CLAUSE ──────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("CLAUSE-BY-CLAUSE ANALYSIS", ST["section"]))
    story.append(HRFlowable(width=W, thickness=0.8, color=C_ACCENT, spaceAfter=10))

    # Sort: High → Medium → Low
    order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_results = sorted(results, key=lambda r: order.get(r["risk"], 3))

    for i, r in enumerate(sorted_results, 1):
        risk      = r["risk"]
        rc        = _risk_color(risk)
        rl        = _risk_light(risk)
        rtxt      = _risk_label_color(risk)
        conf_pct  = int(r["confidence"] * 100)
        clause_tx = r["clause"][:450] + ("..." if len(r["clause"]) > 450 else "")
        expl_tx   = r.get("explanation", "")

        # confidence bar inside badge cell
        conf_bar_w  = 0.9 * cm * (conf_pct / 100)
        conf_bar_track = 0.9 * cm - conf_bar_w

        badge_content = [
            Paragraph(risk, ParagraphStyle(f"rsk_{i}",
                fontSize=7.5, fontName="Helvetica-Bold",
                textColor=rtxt, alignment=TA_CENTER)),
            Paragraph(f"{conf_pct}%", ParagraphStyle(f"pct_{i}",
                fontSize=7, fontName="Helvetica",
                textColor=rtxt, alignment=TA_CENTER)),
        ]

        clause_content = [
            Paragraph(
                f'<font size="7" color="#8888aa">Clause {i}</font>',
                ParagraphStyle(f"cn_{i}", fontSize=7, fontName="Helvetica",
                    textColor=C_MUTED, spaceAfter=3, leading=9)),
            Paragraph(clause_tx, ST["clause"]),
            Spacer(1, 3),
            Paragraph(
                f'<font color="#8888aa"><i>{expl_tx}</i></font>',
                ParagraphStyle(f"ex_{i}", fontSize=8, fontName="Helvetica-Oblique",
                    textColor=C_MUTED, leading=11)),
        ]

        row_data   = [[badge_content, clause_content]]
        row_table  = Table(row_data, colWidths=[1.6*cm, W - 1.8*cm])
        row_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1),  rl),
            ("BACKGROUND",    (1,0), (1,-1),  C_WHITE),
            ("LINEBEFORE",    (0,0), (0,-1),  3,   rc),
            ("BOX",           (0,0), (-1,-1), 0.5, C_BORDER),
            ("LINEAFTER",     (0,0), (0,-1),  0.3, C_BORDER),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",    (0,0), (-1,-1), 9),
            ("BOTTOMPADDING", (0,0), (-1,-1), 9),
            ("LEFTPADDING",   (0,0), (0,-1),  5),
            ("RIGHTPADDING",  (0,0), (0,-1),  5),
            ("LEFTPADDING",   (1,0), (1,-1),  10),
            ("RIGHTPADDING",  (1,0), (1,-1),  8),
            ("ALIGN",         (0,0), (0,-1),  "CENTER"),
        ]))
        story.append(KeepTogether(row_table))
        story.append(Spacer(1, 5))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    footer_data = [[
        Paragraph(
            "This report was generated automatically by the Legal Risk Analyzer using a BERT-based "
            "legal clause classifier and AI-powered summarization. It is for informational purposes ",
            ST["footer"]
        ),
    ]]
    footer_tbl = Table(footer_data, colWidths=[W])
    footer_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("BACKGROUND",    (0,0), (-1,-1), C_BG_LIGHT),
        ("BOX",           (0,0), (-1,-1), 0.3, C_BORDER),
        ("LINEBEFORE",    (0,0), (0,-1),  2,   C_ACCENT),
    ]))
    story.append(footer_tbl)

    doc.build(story)

    # Get bytes from buffer
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Optionally save to disk (local development only)
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
        except Exception:
            pass  # silently skip if filesystem is read-only (Streamlit Cloud)

    return pdf_bytes, filename