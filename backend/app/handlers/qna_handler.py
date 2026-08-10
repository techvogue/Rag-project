from app.services.llm_service import stream_answer
from app.services.fallback_service import fallback_answer
from app.models.qna_model import QADocument, QAItem
from datetime import datetime, timezone
from app.models.user_model import User

async def process_qa_stream(document_id: str, question: str, current_user: User):
    # Fetch or create the document for storing Q&A FIRST so we can use it as memory
    qaDocument = await QADocument.find_one(QADocument.document_id == str(document_id))
    if not qaDocument:
        qaDocument = QADocument(
            document_id=str(document_id),
            qas=[],
            total_qas=0
        )

    full_answer = ""
    used_fallback = False
    
    try:
        # Stream chunks from the LLM service
        async for chunk in stream_answer(question, str(document_id), qaDocument.qas):
            full_answer += chunk
            yield chunk 
    except Exception as e:
        print(f"LLM error: {e}")
        fallback = await fallback_answer(question)
        full_answer = fallback
        used_fallback = True
        yield fallback

    # Append the new QA pair to DB after streaming completes
    qa_item = QAItem(
        question=question,
        answer=full_answer,
        timestamp=datetime.now(timezone.utc),
        used_fallback=used_fallback,
        sources=None,
    )
    qaDocument.qas.append(qa_item)
    qaDocument.total_qas += 1
    await qaDocument.save()
    
    # Also update user stats here since we no longer do it in the router
    current_user.total_qna += 1
    await current_user.save()
