"""
Document Splitting Module.
Splits text into chunks and generates chunk statistics for evaluation and comparison.
"""

from typing import List, Dict, Any, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def split_documents(
    documents: List[Document], 
    chunk_size: int = 500, 
    chunk_overlap: int = 100
) -> List[Document]:
    """
    Splits documents into smaller text chunks using RecursiveCharacterTextSplitter.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    # Add index and config tracking to chunk metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
        chunk.metadata["chunk_size_config"] = chunk_size
        chunk.metadata["chunk_overlap_config"] = chunk_overlap
    return chunks

def calculate_chunk_metrics(chunks: List[Document]) -> Dict[str, Any]:
    """
    Calculates statistics (count, average size, min/max size, previews) for document chunks.
    """
    if not chunks:
        return {
            "chunk_count": 0,
            "avg_chunk_size": 0.0,
            "largest_chunk": 0,
            "smallest_chunk": 0,
            "previews": []
        }
        
    sizes = [len(chunk.page_content) for chunk in chunks]
    previews = []
    # Extract up to 3 sample chunks for previewing
    for i in range(min(3, len(chunks))):
        previews.append({
            "index": chunks[i].metadata.get("chunk_index", i),
            "source": chunks[i].metadata.get("source", "Unknown"),
            "size": len(chunks[i].page_content),
            "content": chunks[i].page_content[:250] + "..." if len(chunks[i].page_content) > 250 else chunks[i].page_content
        })
        
    return {
        "chunk_count": len(chunks),
        "avg_chunk_size": sum(sizes) / len(sizes),
        "largest_chunk": max(sizes),
        "smallest_chunk": min(sizes),
        "previews": previews
    }

def run_chunking_experiments(documents: List[Document], overlap: int = 100) -> Dict[int, Dict[str, Any]]:
    """
    Performs chunking experiments across predefined chunk sizes (300, 500, 700).
    """
    sizes = [300, 500, 700]
    experiment_results = {}
    for size in sizes:
        chunks = split_documents(documents, chunk_size=size, chunk_overlap=overlap)
        metrics = calculate_chunk_metrics(chunks)
        experiment_results[size] = {
            "chunks": chunks,
            "metrics": metrics
        }
    return experiment_results
