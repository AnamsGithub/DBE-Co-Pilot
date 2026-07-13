import json
from pathlib import Path

_companies = []

DATA_PATH = Path(__file__).parent.parent / "data" / "companies.json"


def load_index():
    global _companies
    with open(DATA_PATH) as f:
        _companies = json.load(f)


def get_company_by_name(name: str) -> dict | None:
    return next((c for c in _companies if c["name"].lower() == name.lower()), None)


def get_all_companies() -> list[dict]:
    return list(_companies)


def get_companies_by_ctc(ctc_label: str) -> list[dict]:
    return [c for c in _companies if c.get("ctc", "") == ctc_label]


def search_companies(query: str, top_k: int = 5) -> list[dict]:
    # Fallback: return all companies if a specific lookup fails
    return list(_companies)
