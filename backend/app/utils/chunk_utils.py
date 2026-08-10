from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

async def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into semantic chunks using LangChain's RecursiveCharacterTextSplitter.
    It splits by paragraphs first, then sentences, preserving context much better than raw slicing.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_text(text)
    return chunks
