import json
from groq import Groq
from app.config import settings
from app.models.schemas import ResumeData, ResumeAnalysis, CompanyMatch

client = Groq(api_key=settings.groq_api_key)

ROADMAP_PROMPT = """
You are a senior MBA career advisor talking directly to a student. Write like a real person giving genuine advice, not like an AI generating a plan.

Student target: {target_context}

What the student ALREADY has (do NOT recommend these again):
- Skills: {existing_skills}
- Projects and experience: {existing_projects}

Skills they are still missing: {missing_skills}
Weak areas in their resume: {weaknesses}

Write a 4-week plan focused ONLY on what this student does not already have. Do not recommend anything listed under "already has". Each week must address a genuinely new gap.

For each week return:
- week: "Week 1", "Week 2", etc.
- focus: what skill to work on (short, e.g. "SQL for business analysis")
- advice: 2-3 sentences of genuine advice written like you are talking to the student. Be direct and encouraging. No corporate language. No long dashes.
- project: one specific hands-on project they can build that week (be very specific, e.g. "Pull Amazon sales data from Kaggle and build a dashboard showing top categories by revenue, return rate, and seasonal trends"). Make sure it is different from what is already in their CV.

Return ONLY a valid JSON object:
{{
  "roadmap": [
    {{
      "week": "Week 1",
      "focus": "string",
      "advice": "string",
      "project": "string"
    }}
  ]
}}
"""

REWRITE_PROMPT = """
You are an expert resume writer for MBA students.

Rewrite the weakest 3 bullet points from this resume to be more impactful.
Add quantified outcomes where possible. Keep it natural, not AI-sounding. No long dashes.

Original bullet points:
{bullets}

Target context: {target_context}

Return ONLY a valid JSON object with:
- rewrites (list of objects, each with "before" and "after" keys)
"""


def _target_context(target_type: str, target_value: str) -> str:
    return {
        "role":    f"becoming a {target_value}",
        "company": f"joining {target_value}",
        "ctc":     f"achieving a CTC of {target_value}",
        "all":     "broad MBA placement across all industries and roles",
    }.get(target_type, target_value)


def generate_roadmap(
    resume_data: ResumeData,
    analysis: ResumeAnalysis,
    matches: list[CompanyMatch],
    target_type: str,
    target_value: str,
) -> list[dict]:
    all_missing = []
    for m in matches:
        all_missing.extend(m.missing_skills)
    unique_missing = list(dict.fromkeys(all_missing))[:8]

    existing_projects = [(s[:90]) for s in (resume_data.experience + resume_data.projects + resume_data.positions)[:5]]

    cgpa_note = f"MBA CGPA: {resume_data.cgpa}. " if resume_data.cgpa else ""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": ROADMAP_PROMPT.format(
            target_context=cgpa_note + _target_context(target_type, target_value),
            existing_skills=", ".join(resume_data.skills[:15]) if resume_data.skills else "none listed",
            existing_projects="; ".join(existing_projects) if existing_projects else "none listed",
            missing_skills=", ".join(unique_missing) if unique_missing else "none identified",
            weaknesses="; ".join(analysis.weaknesses),
        )}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    data = json.loads(response.choices[0].message.content)
    return data.get("roadmap", [])


def rewrite_bullets(resume_data: ResumeData, target_type: str, target_value: str) -> list[dict]:
    bullets = (resume_data.experience[:3] + resume_data.projects[:2])[:3]

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": REWRITE_PROMPT.format(
            bullets="\n".join(f"- {b}" for b in bullets),
            target_context=_target_context(target_type, target_value),
        )}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    data = json.loads(response.choices[0].message.content)
    return data.get("rewrites", [])
