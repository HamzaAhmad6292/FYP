from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from services.llm_service import LLMService
from services.visualizer import VisualizationService
import pdfkit
import tempfile

router = APIRouter(tags=["Reports"])

@router.get("/report/html", response_class=HTMLResponse)
async def generate_html_report(insights: dict, predictions: dict):
    try:
        llm = LLMService()
        report_content = await llm.generate_report(insights, predictions)
        return f"""
        <html>
            <head><title>Business Report</title></head>
            <body>
                {report_content}
            </body>
        </html>
        """
    except Exception as e:
        raise HTTPException(500, f"Report generation failed: {str(e)}")

@router.get("/report/pdf")
async def generate_pdf_report(insights: dict, predictions: dict):
    try:
        html = await generate_html_report(insights, predictions)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            pdfkit.from_string(html, f.name)
            return FileResponse(f.name, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(500, f"PDF generation failed: {str(e)}")