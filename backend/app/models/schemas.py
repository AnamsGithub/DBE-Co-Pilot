from pydantic import BaseModel
from typing import Optional


class ResumeData(BaseModel):
    name: str
    cgpa: str = ""
    education: list[str]
    experience: list[str]
    skills: list[str]
    certifications: list[str]
    achievements: list[str]
    projects: list[str]
    positions: list[str] = []


class ResumeAnalysis(BaseModel):
    score: int
    strengths: list[str]
    weaknesses: list[str]
    improvements: list[str]


class CompanyMatch(BaseModel):
    company_name: str
    role: str
    match_score: int
    matched_skills: list[str]
    missing_skills: list[str]


class CareerReport(BaseModel):
    resume_data: ResumeData
    analysis: ResumeAnalysis
    target_type: str   # role | company | ctc | all
    target_value: str
    company_matches: list[CompanyMatch]
    skill_roadmap: list[dict]
    rewritten_bullets: list[dict]


class AnalyzeRequest(BaseModel):
    target_type: str = "role"   # role | company | ctc | all
    target_value: str = ""
    session_id: Optional[str] = None


class DBEResumeData(BaseModel):
    filename: str = ""
    name: str
    gender: str
    age: str
    languages: str
    email: str
    phone: str
    tagline: str
    education: list[dict]
    experience: list[dict]
    internships: list[dict]
    projects: list[dict]
    positions: list[dict]
    academic_achievements: list[str]
    competition_achievements: list[str]
    certifications: list[str]
    interests: list[str]
    skills: list[str]


class ComplianceIssue(BaseModel):
    section: str
    field: str
    issue: str
    suggestion: str


class PointerImprovement(BaseModel):
    section: str
    original: str
    improved: str
    reason: str


class CVReport(BaseModel):
    student_name: str
    filename_ok: bool
    compliance_issues: list[ComplianceIssue]
    pointer_improvements: list[PointerImprovement]


class CVRequest(BaseModel):
    session_id: str
    filename: str = ""
