You are a senior AI engineer and product architect. Help me build an Agentic AI project called:

# CareerCopilot AI

## An AI-powered placement preparation assistant for MBA students

## Product Vision

Build an autonomous AI career assistant that analyzes a student's resume, understands their career goals, compares them with campus hiring trends and job requirements, identifies skill gaps, and creates a personalized improvement roadmap.

The target users are MBA students preparing for placements.

The goal is not just resume analysis — it should behave like a career advisor powered by multiple AI agents.

---

# Core User Flow

1. Student uploads resume PDF.

2. System extracts:

- Name
- Education
- Work experience
- Internships
- Projects
- Skills
- Certifications
- Achievements

3. Student selects target role:
   Examples:

- Business Analyst
- Product Manager
- Marketing Analyst
- Finance Analyst
- Consultant

4. AI agents analyze:

## Agent 1: Resume Analysis Agent

Responsibilities:

- Parse resume
- Evaluate quality
- Identify strengths and weaknesses
- Score resume out of 100
- Check ATS compatibility
- Suggest improvements

Output example:

Resume Score: 78/100

Strengths:

- Strong analytics background
- Good technical projects

Weakness:

- Missing quantified achievements
- Lack of SQL/PowerBI keywords

---

## Agent 2: Company Matching Agent

Create a company knowledge base containing:

Company name
Roles hired
Required skills
Typical job descriptions
Selection process

The agent should compare student profile with company requirements.

Output:

Recommended companies:

Deloitte
Role: Business Analyst
Match Score: 84%

Why:

- Python experience
- Analytics projects

Missing:

- SQL
- PowerBI

---

## Agent 3: Career Improvement Agent

Based on analysis:

Generate:

Resume improvements:
Before:
"Worked on customer analysis"

After:
"Analyzed customer datasets using Python to identify behavioral patterns and improve decision-making."

Skill roadmap:

Week 1:
Learn SQL basics

Week 2:
Build analytics dashboard

Week 3:
Practice business cases

---

# Future Agents (design architecture to allow expansion)

Interview Coach Agent:

- Generate interview questions
- Mock interviews
- HR preparation

Application Strategy Agent:

- Recommend companies
- Track applications

Networking Agent:

- Suggest LinkedIn outreach messages

---

# Technical Requirements

Build this as a full-stack application.

Frontend:
React + Tailwind CSS

Backend:
Python FastAPI

AI Layer:
Use LangGraph for agent orchestration.

LLM:
Support OpenAI API initially but keep architecture flexible.

Document Processing:
PyMuPDF/pdfplumber for PDF extraction.

Database:
PostgreSQL

Vector Database:
FAISS or ChromaDB for company/job knowledge retrieval.

---

# Architecture Requirement

Design it using an agentic workflow:

User Input
|
Career Manager Agent
|

-

| | |
Resume Agent Company Agent Skill Gap Agent
|
Improvement Agent
|
Final Career Report

---

# MVP Scope (build this first)

Do NOT over-engineer.

Phase 1:

- Upload resume PDF
- Extract information
- Resume scoring
- Basic company matching
- Generate improvement report

Phase 2:

- Add company database
- Add RAG
- Add more agents

Phase 3:

- Add interview preparation

---

# UI Requirements

Create a professional SaaS-style dashboard.

Pages:

1. Landing page

- Product explanation
- Features

2. Resume Upload

3. Analysis Dashboard

Show:

- Resume score
- Skill match
- Recommended roles
- Improvement suggestions

4. Career Roadmap

---

# Development Approach

First:

1. Explain architecture
2. Create folder structure
3. Setup backend
4. Setup frontend
5. Build MVP step-by-step

Do not dump all code at once.

Act as my technical co-founder:

- Make good engineering decisions
- Explain tradeoffs
- Keep code production-quality
- Prioritize working MVP first

Start by creating the project architecture and folder structure.
