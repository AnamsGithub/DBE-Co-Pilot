import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import resume, career
from app.tools.vector_store import load_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_index()
    yield


app = FastAPI(title="DBECopilot AI", version="1.0.0", lifespan=lifespan)

# FRONTEND_URL can be set to your Vercel URL in production
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
app.include_router(career.router, prefix="/api/career", tags=["Career"])


@app.get("/health")
def health():
    return {"status": "ok"}
