from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId
from fastapi.responses import StreamingResponse

from app.schemas.qna_schema import QADocumentSchema, QAItemSchema
from app.models.user_model import User
from app.utils.get_current_user import get_current_user
from app.handlers.qna_handler import process_qa_stream
from app.models.document_model import DocumentModel
from app.models.qna_model import QADocument

router = APIRouter()

@router.post("/ask")
async def ask_question(
    body: dict,
    current_user: User = Depends(get_current_user)
):
    document_id_raw = body.get("document_id")
    question = body.get("question")

    if not document_id_raw or not question:
        raise HTTPException(status_code=400, detail="Missing document_id or question")

    try:
        document_id = PydanticObjectId(document_id_raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid document ID format")

    document = await DocumentModel.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    # Return the generator as a plain text stream
    return StreamingResponse(
        process_qa_stream(document_id, question, current_user), 
        media_type="text/plain"
    )

@router.get("/qnaInitial", response_model=List[QAItemSchema])
async def get_recent_qnas(document_id: str):
    document = await QADocument.find_one(QADocument.document_id == document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return the 3 most recent Q&As
    recent_qnas = sorted(document.qas, key=lambda qa: qa.timestamp, reverse=True)[:3]
    return recent_qnas


@router.get("/qnaAll", response_model=List[QAItemSchema])
async def get_all_qnas(document_id: str):
    document = await QADocument.find_one(QADocument.document_id == document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return all Q&As sorted by timestamp (oldest first)
    all_qnas = sorted(document.qas, key=lambda qa: qa.timestamp)
    return all_qnas
