import os
from typing import List, Any
from dotenv import load_dotenv
from langchain_cohere import ChatCohere
from langchain_core.prompts import PromptTemplate
from app.vectorstore.faiss_index import search_faiss_by_document

load_dotenv()

# Initialize LangChain ChatCohere model
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
llm = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    model="command",
    temperature=0.7,
    max_tokens=250
)

# Function to generate a response using Cohere in a streaming fashion
async def stream_answer(query: str, document_id: str, chat_history: List[Any] = None):
    """
    Get the answer from Cohere by performing semantic search on the document and yielding chunks.
    """
    top_k = 5
    search_results = await search_faiss_by_document(document_id, query, top_k)

    if not search_results:
        yield "Sorry, I couldn't find relevant information in the document."
        return

    # Combine the text from the most relevant chunks with Source tags
    context_parts = []
    for i, result in enumerate(search_results):
        context_parts.append(f"[Source {i+1}]:\n{result['text']}")
        
    context = "\n\n".join(context_parts)

    # Format the past 3 turns into a string for memory
    history_text = "No previous chat history."
    if chat_history and len(chat_history) > 0:
        history_text = ""
        for qa in chat_history[-3:]:
            history_text += f"User: {qa.question}\nAI: {qa.answer}\n\n"

    # Prepare the prompt with context, history, and the query
    prompt_template = PromptTemplate.from_template(
        "You are an AI assistant answering questions based on the provided document context.\n"
        "IMPORTANT: When you use information from the context, you MUST cite the source using the [Source X] format at the end of the relevant sentence.\n\n"
        "--- Chat History ---\n{history}\n"
        "--- Document Context ---\n{context}\n\n"
        "--- Current Question ---\n{query}\n\n"
        "Answer:"
    )
    
    prompt_value = prompt_template.invoke({
        "context": context,
        "history": history_text,
        "query": query
    })

    try:
        # Use LangChain to stream the answer
        async for chunk in llm.astream(prompt_value):
            yield chunk.content
            
        # After the LLM finishes, yield the sources at the bottom!
        yield "\n\n---\n**Sources used:**\n"
        for i, result in enumerate(search_results):
            # Show a snippet of the source
            snippet = result['text'][:150].replace('\n', ' ') + "..."
            yield f"- **[Source {i+1}]**: {snippet}\n"

    except Exception as e:
        print(f"Error generating answer: {e}")
        yield "Sorry, there was an issue generating the answer. Please try again later."
