import re
import json
from groq import Groq
from app.config import settings
from app.models.schemas import DBEResumeData, ComplianceIssue, PointerImprovement

client = Groq(api_key=settings.groq_api_key)

# Empirical character limits from actual DBE-DU CVs at Arial 12pt
MAX_CHARS = 105
MIN_CHARS = 79  # 3/4 of MAX_CHARS


# ── Format compliance checks ──────────────────────────────────────────────────

def _check_naming_convention(filename: str) -> bool:
    """Firstname_Lastname_CV.pdf"""
    name = filename.replace(".pdf", "").replace(".xlsx", "")
    parts = name.split("_")
    return len(parts) >= 3 and parts[-1].upper() == "CV"


def _is_pure_date_string(date_str: str) -> bool:
    """Return True only if the string starts with a month abbreviation.
    Guards against LLM mis-extraction like "Concentrix Representative-Operations Feb’24 – Aug’24"
    where role/company text gets merged into the dates field.
    """
    month_pattern = r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[‘’]\d{2}"
    return bool(re.match(month_pattern, date_str.strip()))


def _check_date_format(date_str: str) -> bool:
    """Acceptable: Jun’25, Jul’25 – Present, Jan’25 – Mar’26
    Apostrophe may be straight (U+0027) or right single quote (U+2019).
    Dash may be hyphen, en-dash, or em-dash.
    """
    month_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[‘’]\d{2}"
    return bool(re.search(month_pattern, date_str))


def _check_duration_format(duration: str) -> bool:
    """Must be '02 Months', '07 Weeks', etc. — two digit number."""
    return bool(re.match(r"^\d{2}\s+(Months|Weeks)$", duration.strip()))


def _ends_with_fullstop(text: str) -> bool:
    return text.strip().endswith(".")


def run_compliance_checks(data: DBEResumeData) -> tuple[bool, list[ComplianceIssue]]:
    issues: list[ComplianceIssue] = []

    # Naming convention
    filename_ok = _check_naming_convention(data.filename) if data.filename else True
    if not filename_ok:
        issues.append(ComplianceIssue(
            section="File",
            field="filename",
            issue=f"'{data.filename}' does not follow Firstname_Lastname_CV format",
            suggestion=f"Rename to {data.name.replace(' ', '_')}_CV.pdf",
        ))

    # Experience duration & date formats
    for exp in data.experience:
        if exp.get("duration") and not _check_duration_format(exp["duration"]):
            issues.append(ComplianceIssue(
                section="Professional Experience",
                field="duration",
                issue=f"'{exp['duration']}' — duration must be in XX Months / XX Weeks format",
                suggestion="Use two-digit format, e.g. '06 Months' not '6 months'",
            ))
        if exp.get("dates") and _is_pure_date_string(exp["dates"]) and not _check_date_format(exp["dates"]):
            issues.append(ComplianceIssue(
                section="Professional Experience",
                field="dates",
                issue=f"'{exp['dates']}' — dates must use Mon'YY format",
                suggestion="e.g. Dec'24 – May'25",
            ))

    # Internship duration & date formats
    for intern in data.internships:
        if intern.get("duration") and not _check_duration_format(intern["duration"]):
            issues.append(ComplianceIssue(
                section="Internship",
                field="duration",
                issue=f"'{intern['duration']}' — duration must be in XX Months / XX Weeks format",
                suggestion="Use two-digit format, e.g. '07 Weeks' not '7 Weeks'",
            ))
        if intern.get("dates") and _is_pure_date_string(intern["dates"]) and not _check_date_format(intern["dates"]):
            issues.append(ComplianceIssue(
                section="Internship",
                field="dates",
                issue=f"'{intern['dates']}' — dates must use Mon'YY format",
                suggestion="e.g. Jun'25 – Jul'25",
            ))

    # Positions dates
    for pos in data.positions:
        if pos.get("dates") and pos["dates"] != "Present" and _is_pure_date_string(pos["dates"]) and not _check_date_format(pos["dates"]):
            issues.append(ComplianceIssue(
                section="Positions of Responsibilities",
                field="dates",
                issue=f"'{pos['dates']}' — dates must use Mon'YY format",
                suggestion="e.g. Sep'25 – Present",
            ))

    # Full stops at end of pointers
    all_bullets = []
    for exp in data.experience:
        all_bullets += [(f"Professional Experience — {exp.get('company', '')}", b) for b in exp.get("bullets", [])]
    for intern in data.internships:
        all_bullets += [(f"Internship — {intern.get('company', '')}", b) for b in intern.get("bullets", [])]
    for proj in data.projects:
        all_bullets += [(f"Key Projects — {proj.get('name', '')}", b) for b in proj.get("bullets", [])]
    for pos in data.positions:
        all_bullets += [(f"Positions — {pos.get('role', '')}", b) for b in pos.get("bullets", [])]
    all_bullets += [("Achievements", b) for b in data.academic_achievements + data.competition_achievements + data.certifications]

    for section, bullet in all_bullets:
        if _ends_with_fullstop(bullet):
            issues.append(ComplianceIssue(
                section=section,
                field="pointer",
                issue=f"Full stop at end: '{bullet[:60]}...'",
                suggestion="Remove the full stop at the end of this pointer",
            ))

    return filename_ok, issues


# ── Pointer length optimisation ───────────────────────────────────────────────

IMPROVE_PROMPT = """
You are a CV editor for MBA students at Department of Business Economics, University of Delhi.

The CV uses Arial 12pt font. Each bullet point cell fits exactly {max_chars} characters on one line.
A bullet point that is shorter than {min_chars} characters is considered too short — it leaves too much whitespace.

Rules:
- DO NOT change: names, dates, company names, institutions, section headers, tagline, education table, skills, interests, positions of responsibility titles
- SKIP entirely any line that looks like a designation or company header — e.g. "Media Analyst Intern, Meltwater" or "Junior Joint Secretary, Student Body, DBE" or "Entrepreneur, Caravan Rental Business". These are NOT bullet sentences.
- ONLY improve the bullet point SENTENCES listed below
- For each bullet: if it is under {min_chars} characters → expand it to {target_chars}-{max_chars} characters by adding specific, realistic detail (quantify outcomes, add method, add tool used)
- For each bullet: if it exceeds {max_chars} characters → trim it to fit within {max_chars} characters without losing the key achievement
- The improved bullet must fit on exactly ONE line — no line breaks, no overflow
- Keep the same meaning and voice
- No full stops at the end

Bullets to improve (section | original text | length):
{bullets_json}

Return ONLY a valid JSON object:
{{
  "improvements": [
    {{"section": "string", "original": "string", "improved": "string", "reason": "string"}}
  ]
}}

Only include bullets that actually need changing. If a bullet is already the right length, skip it.
"""


_DATE_IN_TEXT = re.compile(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)['']\d{2}")

# Action verbs that real CV bullets start with
_ACTION_VERB_START = re.compile(
    r"^(Managed|Developed|Led|Built|Designed|Analysed|Analyzed|Created|Implemented|"
    r"Conducted|Prepared|Coordinated|Assisted|Supported|Handled|Executed|Delivered|"
    r"Achieved|Generated|Increased|Reduced|Improved|Researched|Identified|Collaborated|"
    r"Worked|Spearheaded|Drove|Streamlined|Oversaw|Monitored|Trained|Mentored|"
    r"Launched|Established|Negotiated|Presented|Drafted|Compiled|Evaluated|"
    r"Contributed|Facilitated|Initiated|Optimized|Optimised|Tracked|Reported|"
    r"Performed|Operated|Processed|Reviewed|Planned|Organized|Organised)",
    re.IGNORECASE
)


def _is_header_line(text: str) -> bool:
    """True if the text looks like a designation/company header mis-extracted as a bullet.
    Catches: lines with Mon'YY dates, and 'Role, Company' noun phrases with no action verb.
    """
    if _DATE_IN_TEXT.search(text):
        return True
    # If it contains a comma but does NOT start with a known action verb, treat as header
    if "," in text and not _ACTION_VERB_START.match(text.strip()):
        return True
    return False


def improve_pointers(data: DBEResumeData) -> list[PointerImprovement]:
    candidates = []

    def collect(section: str, bullets: list[str]):
        for b in bullets:
            if not _is_header_line(b):
                candidates.append({"section": section, "original": b, "length": len(b)})

    for exp in data.experience:
        collect(f"Professional Experience — {exp.get('company', '')}", exp.get("bullets", []))
    for intern in data.internships:
        collect(f"Internship — {intern.get('company', '')}", intern.get("bullets", []))
    for proj in data.projects:
        collect(f"Key Projects — {proj.get('name', '')}", proj.get("bullets", []))
    for pos in data.positions:
        collect(f"Positions — {pos.get('role', '')}", pos.get("bullets", []))

    if not candidates:
        return []

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": IMPROVE_PROMPT.format(
            max_chars=MAX_CHARS,
            min_chars=MIN_CHARS,
            target_chars=MIN_CHARS + 10,
            bullets_json=json.dumps(candidates, indent=2),
        )}],
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    data_out = json.loads(response.choices[0].message.content)
    return [PointerImprovement(**item) for item in data_out.get("improvements", [])]
