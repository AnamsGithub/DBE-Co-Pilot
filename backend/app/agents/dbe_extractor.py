import json
from groq import Groq
from app.config import settings
from app.models.schemas import DBEResumeData

client = Groq(api_key=settings.groq_api_key)

EXTRACT_PROMPT = """
You are parsing a CV from Department of Business Economics, University of Delhi (DBE-DU).
All DBE-DU CVs follow a strict fixed format. Extract every field exactly as written — do NOT rephrase, reorder, or correct anything.

## DBE-DU CV Structure (in order):

**Header:**
- Name (large text, top left)
- Gender, Age | Languages
- Email | Phone | Department

**Tagline bar:** one-line summary (e.g. "VP Student Body | HackerRank SQL 5 Star | Analytics")

**Educational Qualifications table** (latest first):
- Each row: degree | year | institution | grade

**Professional Experience** (optional section):
- Duration shown as "XX Months" or "XX Weeks" on right
- Each entry: company | role | date range
- Followed by bullet point responsibilities

**Internship** (optional section):
- Same structure as Professional Experience

**Key Projects** (optional section):
- Each project: name (left) | bullet points | skill_tag (right, e.g. "SQL", "Machine Learning")

**Positions of Responsibilities:**
- Each entry: role (left) | bullets | date range (right)

**Achievements:**
- Academic Achievements: bullet list
- Competitions/Events: bullet list
- Certifications: bullet list

**Interests:** pipe-separated list
**Skills:** pipe-separated list

---

Now extract the following CV. Return ONLY a valid JSON object with this exact structure:

{{
  "name": "string",
  "gender": "string",
  "age": "string",
  "languages": "string",
  "email": "string",
  "phone": "string",
  "tagline": "string",
  "education": [
    {{"degree": "string", "year": "string", "institution": "string", "grade": "string"}}
  ],
  "experience": [
    {{"company": "string", "role": "string", "duration": "string", "dates": "string", "bullets": ["string"]}}
  ],
  "internships": [
    {{"company": "string", "role": "string", "duration": "string", "dates": "string", "bullets": ["string"]}}
  ],
  "projects": [
    {{"name": "string", "bullets": ["string"], "skill_tag": "string"}}
  ],
  "positions": [
    {{"role": "string", "bullets": ["string"], "dates": "string"}}
  ],
  "academic_achievements": ["string"],
  "competition_achievements": ["string"],
  "certifications": ["string"],
  "interests": ["string"],
  "skills": ["string"]
}}

CV Text:
{cv_text}
"""


def extract_dbe_resume(cv_text: str, filename: str = "") -> DBEResumeData:
    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[{"role": "user", "content": EXTRACT_PROMPT.format(cv_text=cv_text)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    data = json.loads(response.choices[0].message.content)
    data["filename"] = filename
    return DBEResumeData(**data)
