import json
import re
from groq import Groq
from app.config import settings
from app.models.schemas import ResumeData, ResumeAnalysis

client = Groq(api_key=settings.groq_api_key)

EXTRACT_PROMPT = """
You are a resume parser for DBE-DU (Delhi University) MBA students.
Extract structured information from the resume text below.
Return ONLY a valid JSON object with these exact keys:

- name (string)
- cgpa (string): MBA CGPA from the student's current degree. Look for patterns like "7.8 CGPA", "8.2/10", "78%", "CGPA: 7.5". Return the raw value found (e.g. "7.8" or "7.8/10"). If not found, return empty string.
- education (list of strings): degrees, institutions, years
- experience (list of strings): for each role, include company name and job title followed by its bullet sentences. E.g. "Concentrix, Operations Rep: Handled customer escalations..." — include company/role so we know the domain. Skip lines that are purely date ranges.
- skills (list of strings)
- certifications (list of strings)
- achievements (list of strings)
- projects (list of strings): for each project, include the project name followed by its bullet sentences. E.g. "Financial Modelling Project: Built a 3-statement model to forecast revenue..." — include project name so we know what the student has already done.
- positions (list of strings): Positions of Responsibility section — include the role title, organisation, and any bullet sentences. E.g. "Vice President, Student Body, DBE-DU: Led placement committee, organised annual fest..." — this is critical for assessing leadership.

Resume text:
{resume_text}
"""

ANALYZE_PROMPT = """
You are a strict MBA placement advisor at DBE-DU. Score this resume honestly.

Target: {target_context}
MBA CGPA: {cgpa}

Resume:
{resume_json}

SCORING RUBRIC (total 100 pts, sum all sections then clamp to 0-100):

1. CGPA (-15 to +25) — label is pre-computed above, use it directly:
   exceptional/topper:+25 | strong/top10%:+20 | good/top25%:+15 | above average:+10 | average:+5 | below average:0 | weak:-5 | poor:-10 | very poor:-15 | not mentioned:0

2. Work Experience (20 pts):
   MNC/Big4/known brand + relevant role:17-20 | mid-tier or partial match:11-16 | any paid work:6-10 | none:0-5

3. POR (15 pts, score highest role held):
   President:14-15 | Joint Secretary:12-13 | VP:11-12 | Jr Joint Secretary:9-10 | Sr Treasurer:7-8 | Jr Treasurer:5-6 | CR:3-4 | Coordinator:1-2 | None:0

4. Projects (15 pts):
   Python/ML/SQL/PowerBI + business impact:12-15 | Excel-based:7-11 | basic/descriptive:3-6 | none:0

5. Achievements (10 pts, score highest found):
   National rank/winner:9-10 | State rank/96%ile:7-8 | City/University:4-6 | College:3-4 | Extracurricular/School:1-2 | None:0

6. Quantitative Impact (8 pts):
   70%+ bullets have numbers:7-8 | 30-70%:4-6 | under 30%:1-3 | none:0

7. Relevant Skills (5 pts, only skills relevant to target count):
   5+:4-5 | 3-4:2-3 | 1-2:1 | none/irrelevant:0

8. Prior Degree (2 pts):
   Reputed institution:2 | average:1 | not mentioned:0

Rules:
- No score for formatting, layout, or template. Content only.
- Do not penalise designation header lines like "VP, Student Body" — those are titles.
- Always mention CGPA in strengths or weaknesses. Do not use scoring mechanics language in output.

Return ONLY a valid JSON object:
{{
  "score": <integer 0-100>,
  "strengths": [<max 3 specific strengths>],
  "weaknesses": [<max 4 specific weaknesses>],
  "improvements": [<3-4 specific actionable steps>]
}}
"""


def _cgpa_label(cgpa_str: str) -> str:
    nums = re.findall(r'\d+\.?\d*', cgpa_str)
    if not nums:
        return "not mentioned"
    val = float(nums[0])
    if val > 10:
        val = val / 10
    if val > 8.5: return "exceptional — topper bracket"
    if val > 8.0: return "strong — top 10%"
    if val > 7.5: return "good — top 25%"
    if val > 7.0: return "above average"
    if val > 6.5: return "average"
    if val > 6.0: return "below average for placements"
    if val > 5.5: return "weak"
    if val > 5.0: return "poor"
    return "very poor"


def _compact_resume(resume_data: ResumeData) -> str:
    """Compact JSON with truncated lists to save tokens."""
    d = {
        "name": resume_data.name,
        "cgpa": resume_data.cgpa,
        "education": resume_data.education[:2],
        "experience": [s[:110] for s in resume_data.experience[:4]],
        "projects": [s[:110] for s in resume_data.projects[:3]],
        "positions": [s[:110] for s in resume_data.positions[:3]],
        "achievements": resume_data.achievements[:4],
        "skills": resume_data.skills[:15],
        "certifications": resume_data.certifications[:4],
    }
    return json.dumps(d, separators=(',', ':'))


def extract_resume_data(resume_text: str) -> ResumeData:
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": EXTRACT_PROMPT.format(resume_text=resume_text)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    return ResumeData(**data)


def analyze_resume(resume_data: ResumeData, target_type: str, target_value: str) -> ResumeAnalysis:
    target_context = {
        "role":    f"Student wants to become a {target_value}",
        "company": f"Student is specifically targeting {target_value}",
        "ctc":     f"Student is targeting a CTC of {target_value}",
        "all":     "Broad MBA placement — identify best-fit companies and roles",
    }.get(target_type, f"Student is targeting {target_value}")

    if resume_data.positions:
        target_context += f". POR: {'; '.join(resume_data.positions[:2])}"

    cgpa_display = f"{resume_data.cgpa} — {_cgpa_label(resume_data.cgpa)}" if resume_data.cgpa else "not mentioned"

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": ANALYZE_PROMPT.format(
            target_context=target_context,
            cgpa=cgpa_display,
            resume_json=_compact_resume(resume_data),
        )}],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    data = json.loads(response.choices[0].message.content)
    return ResumeAnalysis(**data)
