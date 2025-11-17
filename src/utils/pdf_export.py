"""
PDF export utilities for generating diagnostic reports.

Provides functionality to export diagnostic results as professional PDF reports.
"""

from typing import List, Optional
from datetime import datetime
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        PageBreak,
        Image as RLImage,
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from loguru import logger


class DiagnosticPDFReport:
    """
    Generate professional PDF reports for diagnostic results.

    Requires reportlab library to be installed.
    """

    def __init__(self):
        """Initialize PDF report generator"""
        if not REPORTLAB_AVAILABLE:
            logger.warning("reportlab not installed. PDF export will not be available.")
            logger.info("Install with: pip install reportlab")

    def generate_report(
        self,
        patient_case: dict,
        diagnostic_result: dict,
        report_type: str = "physician_summary",
    ) -> Optional[BytesIO]:
        """
        Generate a PDF report for diagnostic results.

        Args:
            patient_case: Patient case data dictionary
            diagnostic_result: Diagnostic result data dictionary
            report_type: Type of report (physician_summary, patient_friendly, detailed_clinical)

        Returns:
            BytesIO buffer containing PDF data, or None if generation fails
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("Cannot generate PDF: reportlab not installed")
            return None

        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
            )

            # Container for the 'Flowable' objects
            elements = []

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                alignment=TA_CENTER,
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#2c5282'),
                spaceAfter=12,
                spaceBefore=12,
            )

            # Add title
            if report_type == "patient_friendly":
                title = Paragraph("Your Diagnostic Report", title_style)
            else:
                title = Paragraph("Clinical Diagnostic Report", title_style)

            elements.append(title)
            elements.append(Spacer(1, 0.2 * inch))

            # Add report metadata
            metadata_data = [
                ["Report Generated:", datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
                ["Case ID:", patient_case.get("case_id", "N/A")],
                ["Review Tier:", f"Tier {diagnostic_result.get('review_tier', 'N/A')}"],
            ]

            metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
            metadata_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            elements.append(metadata_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Add patient information section
            elements.append(Paragraph("Patient Information", heading_style))

            patient_data = [
                ["Age:", f"{patient_case.get('age', 'N/A')} years"],
                ["Sex:", patient_case.get('sex', 'N/A').capitalize()],
                ["Chief Complaint:", patient_case.get('chief_complaint', 'N/A')],
            ]

            patient_table = Table(patient_data, colWidths=[1.5 * inch, 4.5 * inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#4a5568')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            elements.append(patient_table)
            elements.append(Spacer(1, 0.3 * inch))

            # Add symptoms section
            elements.append(Paragraph("Reported Symptoms", heading_style))

            symptoms = patient_case.get('symptoms', [])
            if symptoms:
                symptom_data = [["Symptom", "Severity", "Duration"]]
                for symptom in symptoms[:10]:  # Limit to first 10
                    symptom_data.append([
                        symptom.get('name', 'N/A').capitalize(),
                        symptom.get('severity', 'N/A').capitalize(),
                        f"{symptom.get('duration_days', 'N/A')} days"
                    ])

                symptom_table = Table(symptom_data, colWidths=[2.5 * inch, 1.75 * inch, 1.75 * inch])
                symptom_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                ]))

                elements.append(symptom_table)
            else:
                elements.append(Paragraph("No symptoms reported.", styles['Normal']))

            elements.append(Spacer(1, 0.3 * inch))

            # Add red flags section if present
            red_flags = diagnostic_result.get('red_flags', [])
            if red_flags:
                elements.append(Paragraph("⚠ RED FLAG ALERT", heading_style))
                for flag in red_flags:
                    flag_text = f"• {flag}"
                    elements.append(Paragraph(flag_text, styles['Normal']))
                elements.append(Spacer(1, 0.2 * inch))

            # Add differential diagnoses
            elements.append(Paragraph("Differential Diagnosis", heading_style))

            diagnoses = diagnostic_result.get('differential_diagnoses', [])
            if diagnoses:
                diag_data = [["Rank", "Condition", "Confidence", "Urgency"]]
                for idx, diagnosis in enumerate(diagnoses[:10], 1):
                    confidence = diagnosis.get('confidence_score', 0)
                    diag_data.append([
                        str(idx),
                        diagnosis.get('condition_name', 'N/A'),
                        f"{int(confidence * 100)}%",
                        diagnosis.get('urgency_level', 'N/A').capitalize()
                    ])

                diag_table = Table(diag_data, colWidths=[0.7 * inch, 3 * inch, 1.2 * inch, 1.1 * inch])
                diag_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
                ]))

                elements.append(diag_table)
            else:
                elements.append(Paragraph("No differential diagnoses available.", styles['Normal']))

            elements.append(Spacer(1, 0.3 * inch))

            # Add recommendations
            elements.append(Paragraph("Recommendations", heading_style))
            recommendations = diagnostic_result.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    rec_text = f"• {rec}"
                    elements.append(Paragraph(rec_text, styles['Normal']))
            else:
                # Default recommendations based on tier
                tier = diagnostic_result.get('review_tier', 4)
                if tier == 1:
                    rec_text = "• Routine follow-up recommended"
                elif tier == 2:
                    rec_text = "• Primary care physician review recommended"
                elif tier == 3:
                    rec_text = "• Specialist consultation recommended"
                else:
                    rec_text = "• Multi-disciplinary team review required"

                elements.append(Paragraph(rec_text, styles['Normal']))

            elements.append(Spacer(1, 0.5 * inch))

            # Add disclaimer
            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#718096'),
                alignment=TA_CENTER,
            )

            disclaimer = Paragraph(
                "<b>DISCLAIMER:</b> This is a Clinical Decision Support tool. "
                "All diagnoses require human review and confirmation by a qualified healthcare professional. "
                "This report should not be used as the sole basis for medical decisions.",
                disclaimer_style
            )
            elements.append(disclaimer)

            # Build PDF
            doc.build(elements)

            # Reset buffer position
            buffer.seek(0)

            logger.info(f"PDF report generated successfully for case {patient_case.get('case_id')}")
            return buffer

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            return None


# Global instance
_pdf_exporter: Optional[DiagnosticPDFReport] = None


def get_pdf_exporter() -> DiagnosticPDFReport:
    """Get or create the global PDF exporter instance"""
    global _pdf_exporter

    if _pdf_exporter is None:
        _pdf_exporter = DiagnosticPDFReport()

    return _pdf_exporter
