import json
import re
from groq import Groq
from app.config import settings
from app.models.schemas import ResumeData, CompanyMatch
from app.tools.vector_store import search_companies, get_companies_by_ctc, get_company_by_name, get_all_companies

client = Groq(api_key=settings.groq_api_key)

MATCH_PROMPT = """
You are an MBA placement expert. Score each company using the formula below. Compute each company independently — do not rank against each other.

STUDENT PROFILE:
CGPA: {student_cgpa}
Skills: {student_skills}
Experience: {student_experience}
Projects: {student_projects}
POR: {student_positions}
Achievements: {student_achievements}

FORMULA (A+B+C+D+E+F, capped 0-100):
A. CGPA (-15 to +25) — use the label in the profile: exceptional:+25 | strong:+20 | good:+15 | above avg:+10 | average:+5 | below avg:0 | weak:-5 | poor:-10 | very poor:-15 | not mentioned:0
B. Domain Skill Fit (25 pts) — evaluate specialist skill alignment, NOT generic skills:
   Generic skills like Excel, PowerPoint, Problem Solving, Communication apply to every MBA student and must NOT be the reason for a high score.
   What matters is specialist domain knowledge — e.g. fund accounting/valuation for Arcesium, equity research/economics for Dolat, SQL/ML for AmEx, credit rating for ICRA.
   Strong specialist match (student's expertise aligns with company's core domain): 20-25
   Good match (clear domain overlap, some specialist gaps): 13-19
   Partial match (general skills apply but missing core specialist knowledge): 6-12
   Weak or no specialist match: 0-5
C. Experience (20 pts) — domain of past work vs company's industry:
   Direct domain match (e.g. finance experience for a finance firm): 17-20
   Adjacent domain (e.g. analytics experience for a data-driven firm): 10-16
   Unrelated domain: 3-9 | No experience: 0
D. POR (15 pts): President:14 | Joint Sec:12 | VP:11 | Jr Joint Sec:9 | Sr Treasurer:7 | Jr Treasurer:5 | CR:3 | Coordinator:1 | None:0
E. Projects (10 pts) — relevance to company's domain:
   Domain-relevant project with Python/ML/SQL/PowerBI: 8-10 | Excel-based domain project: 5-7 | Unrelated/basic: 1-4 | None: 0
F. Achievements (5 pts): National:5 | State/96%ile:4 | City/Uni:3 | College:2 | School/Extra:1 | None:0

Context: {target_context}

Companies:
{companies_json}

Return ONLY a valid JSON object:
{{
  "matches": [
    {{
      "company_name": "<exact name>",
      "role": "<best matching role>",
      "match_score": <integer 0-100>,
      "matched_skills": ["<student skills matching this company>"],
      "missing_skills": ["<required skills student lacks>"]
    }}
  ]
}}
"""


def _get_candidate_companies(target_type: str, target_value: str, resume_data: ResumeData) -> list[dict]:
    if target_type == "company":
        match = get_company_by_name(target_value)
        return [match] if match else search_companies(target_value, top_k=1)

    if target_type == "ctc":
        filtered = get_companies_by_ctc(target_value)
        return filtered if filtered else search_companies(" ".join(resume_data.skills), top_k=5)

    return get_all_companies()


def _trim(items: list[str], count: int, max_chars: int = 120) -> str:
    trimmed = [s[:max_chars] for s in items[:count]]
    return "; ".join(trimmed) or "none listed"


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


def _build_profile(resume_data: ResumeData) -> dict:
    if resume_data.cgpa:
        cgpa = f"{resume_data.cgpa} ({_cgpa_label(resume_data.cgpa)})"
    else:
        cgpa = "not mentioned"
    return {
        "cgpa":        cgpa,
        "skills":      ", ".join(resume_data.skills[:15]) or "none listed",
        "experience":  _trim(resume_data.experience, 3),
        "projects":    _trim(resume_data.projects, 3),
        "positions":   _trim(resume_data.positions, 2),
        "achievements": _trim(resume_data.achievements, 3),
    }


def match_companies(resume_data: ResumeData, target_type: str, target_value: str) -> list[CompanyMatch]:
    candidate_companies = _get_candidate_companies(target_type, target_value, resume_data)
    if not candidate_companies:
        return []

    target_context = {
        "role":    f"Student is targeting a {target_value} role.",
        "company": f"Student is specifically targeting {target_value}.",
        "ctc":     f"Student is targeting companies offering {target_value}.",
        "all":     "General MBA placement — evaluate absolute fit for each company.",
    }.get(target_type, target_value)

    profile = _build_profile(resume_data)

    slim_companies = [
        {"name": c["name"], "ctc": c.get("ctc", ""), "roles": c.get("roles", []), "required_skills": c.get("required_skills", [])}
        for c in candidate_companies
    ]

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": MATCH_PROMPT.format(
            target_context=target_context,
            student_cgpa=profile["cgpa"],
            student_skills=profile["skills"],
            student_experience=profile["experience"],
            student_projects=profile["projects"],
            student_positions=profile["positions"],
            student_achievements=profile["achievements"],
            companies_json=json.dumps(slim_companies, separators=(',', ':')),
        )}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    data = json.loads(response.choices[0].message.content)
    return [CompanyMatch(**m) for m in data.get("matches", [])]
