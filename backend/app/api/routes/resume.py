import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    session_id = str(uuid.uuid4())
    dest = UPLOAD_DIR / f"{session_id}.pdf"

    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    return {"session_id": session_id, "filename": file.filename}
