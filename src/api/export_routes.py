"""
Export functionality for diagnostic reports.

Provides endpoints for exporting reports in various formats (PDF, JSON, CSV).
"""

from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from loguru import logger

from ..models.database import User
from ..models.schemas import PatientCase, DiagnosticResult
from ..services.auth import get_current_user
from ..utils.pdf_export import get_pdf_exporter

router = APIRouter()


@router.post(
    "/pdf",
    status_code=status.HTTP_200_OK,
    summary="Export diagnostic report as PDF",
    description="Generate and download a professional PDF report of diagnostic results",
)
async def export_pdf_report(
    patient_case: PatientCase,
    diagnostic_result: DiagnosticResult,
    report_type: str = "physician_summary",
    current_user: User = Depends(get_current_user),
):
    """
    Generate a PDF report from diagnostic results.

    Args:
        patient_case: Patient case data
        diagnostic_result: Diagnostic results
        report_type: Type of report (physician_summary, patient_friendly, detailed_clinical)

    Returns:
        PDF file as streaming response
    """
    try:
        pdf_exporter = get_pdf_exporter()

        # Convert Pydantic models to dicts
        case_dict = patient_case.model_dump()
        result_dict = diagnostic_result.model_dump()

        # Generate PDF
        pdf_buffer = pdf_exporter.generate_report(
            patient_case=case_dict,
            diagnostic_result=result_dict,
            report_type=report_type,
        )

        if pdf_buffer is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate PDF report. PDF export may not be available."
            )

        # Create filename
        filename = f"diagnostic_report_{patient_case.case_id}_{report_type}.pdf"

        # Return as streaming response
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export PDF report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export PDF report"
        )


@router.post(
    "/json",
    status_code=status.HTTP_200_OK,
    summary="Export diagnostic report as JSON",
    description="Export diagnostic results as JSON for programmatic use",
)
async def export_json_report(
    patient_case: PatientCase,
    diagnostic_result: DiagnosticResult,
    current_user: User = Depends(get_current_user),
):
    """
    Export diagnostic results as JSON.

    Useful for integration with other systems or data analysis.
    """
    try:
        export_data = {
            "patient_case": patient_case.model_dump(),
            "diagnostic_result": diagnostic_result.model_dump(),
            "exported_by": {
                "user_id": current_user.id,
                "username": current_user.username,
                "role": current_user.role.value,
            },
            "export_timestamp": diagnostic_result.analysis_timestamp if hasattr(diagnostic_result, 'analysis_timestamp') else None,
        }

        filename = f"diagnostic_export_{patient_case.case_id}.json"

        return Response(
            content=export_data,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        logger.error(f"Failed to export JSON report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export JSON report"
        )
