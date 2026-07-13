from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from app.tools.pdf_extractor import extract_resume_text
from app.agents.resume_agent import extract_resume_data, analyze_resume
from app.agents.company_agent import match_companies
from app.agents.improvement_agent import generate_roadmap
from app.models.schemas import ResumeData, ResumeAnalysis, CompanyMatch, CareerReport


class AgentState(TypedDict):
    pdf_path: str
    target_type: str
    target_value: str
    raw_text: Optional[str]
    resume_data: Optional[ResumeData]
    analysis: Optional[ResumeAnalysis]
    company_matches: Optional[list[CompanyMatch]]
    skill_roadmap: Optional[list[str]]
    rewritten_bullets: Optional[list[dict]]
    error: Optional[str]


def node_extract_text(state: AgentState) -> AgentState:
    try:
        state["raw_text"] = extract_resume_text(state["pdf_path"])
    except Exception as e:
        state["error"] = f"PDF extraction failed: {e}"
    return state


def node_parse_resume(state: AgentState) -> AgentState:
    if state.get("error"):
        return state
    try:
        state["resume_data"] = extract_resume_data(state["raw_text"])
    except Exception as e:
        state["error"] = f"Resume parsing failed: {e}"
    return state


def node_analyze_resume(state: AgentState) -> AgentState:
    if state.get("error"):
        return state
    try:
        state["analysis"] = analyze_resume(
            state["resume_data"],
            state["target_type"],
            state["target_value"],
        )
    except Exception as e:
        state["error"] = f"Resume analysis failed: {e}"
    return state


def node_match_companies(state: AgentState) -> AgentState:
    if state.get("error"):
        return state
    try:
        state["company_matches"] = match_companies(
            state["resume_data"],
            state["target_type"],
            state["target_value"],
        )
    except Exception as e:
        state["error"] = f"Company matching failed: {e}"
    return state


def node_generate_improvement(state: AgentState) -> AgentState:
    if state.get("error"):
        return state
    try:
        state["skill_roadmap"] = generate_roadmap(
            state["resume_data"],
            state["analysis"],
            state["company_matches"],
            state["target_type"],
            state["target_value"],
        )
        state["rewritten_bullets"] = []
    except Exception as e:
        state["error"] = f"Improvement generation failed: {e}"
    return state


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("extract_text", node_extract_text)
    graph.add_node("parse_resume", node_parse_resume)
    graph.add_node("analyze_resume", node_analyze_resume)
    graph.add_node("match_companies", node_match_companies)
    graph.add_node("generate_improvement", node_generate_improvement)

    graph.set_entry_point("extract_text")
    graph.add_edge("extract_text", "parse_resume")
    graph.add_edge("parse_resume", "analyze_resume")
    graph.add_edge("analyze_resume", "match_companies")
    graph.add_edge("match_companies", "generate_improvement")
    graph.add_edge("generate_improvement", END)

    return graph.compile()


career_graph = build_graph()


def run_career_analysis(pdf_path: str, target_type: str, target_value: str) -> CareerReport:
    initial_state: AgentState = {
        "pdf_path": pdf_path,
        "target_type": target_type,
        "target_value": target_value,
        "raw_text": None,
        "resume_data": None,
        "analysis": None,
        "company_matches": None,
        "skill_roadmap": None,
        "rewritten_bullets": None,
        "error": None,
    }

    final_state = career_graph.invoke(initial_state)

    if final_state.get("error"):
        raise RuntimeError(final_state["error"])

    return CareerReport(
        resume_data=final_state["resume_data"],
        analysis=final_state["analysis"],
        target_type=target_type,
        target_value=target_value,
        company_matches=final_state["company_matches"],
        skill_roadmap=final_state["skill_roadmap"],
        rewritten_bullets=final_state["rewritten_bullets"],
    )
