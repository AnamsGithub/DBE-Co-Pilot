import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyzeRequest, CareerReport, CVRequest, CVReport
from app.agents.manager import run_career_analysis
from app.agents.dbe_extractor import extract_dbe_resume
from app.agents.compliance_agent import run_compliance_checks, improve_pointers
from app.tools.pdf_extractor import extract_resume_text

router = APIRouter()

UPLOAD_DIR = Path("uploads")
COMPANIES_FILE = Path("app/data/companies.json")


@router.get("/companies")
async def get_companies():
    data = json.loads(COMPANIES_FILE.read_text())
    return [c["name"] for c in data]


@router.post("/analyze", response_model=CareerReport)
async def analyze(request: AnalyzeRequest):
    pdf_path = UPLOAD_DIR / f"{request.session_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")
    try:
        report = run_career_analysis(str(pdf_path), request.target_type, request.target_value)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return report


@router.post("/check-cv", response_model=CVReport)
async def check_cv(request: CVRequest):
    pdf_path = UPLOAD_DIR / f"{request.session_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Resume not found. Please upload first.")
    try:
        raw_text = extract_resume_text(str(pdf_path))
        cv_data = extract_dbe_resume(raw_text, filename=request.filename)
        filename_ok, compliance_issues = run_compliance_checks(cv_data)
        pointer_improvements = improve_pointers(cv_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return CVReport(
        student_name=cv_data.name,
        filename_ok=filename_ok,
        compliance_issues=compliance_issues,
        pointer_improvements=pointer_improvements,
    )
