"""
Document Loader Module.
Handles document ingestion from PDFs and TXT files, extracting page counts and characters.
"""

import os
from typing import List, Dict, Any, Tuple
import pdfplumber
from langchain_core.documents import Document

def load_text_file(file_path: str) -> List[Document]:
    """
    Loads a TXT file and returns a list containing a single LangChain Document.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        
    filename = os.path.basename(file_path)
    metadata = {
        "source": filename,
        "page": 1,
        "total_pages": 1,
        "char_count": len(content),
        "file_type": "txt"
    }
    return [Document(page_content=content, metadata=metadata)]

def load_pdf_file(file_path: str) -> List[Document]:
    """
    Loads a PDF file page-by-page using pdfplumber and returns a list of Document objects.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    documents = []
    filename = os.path.basename(file_path)
    
    with pdfplumber.open(file_path) as pdf:
        total_pages = len(pdf.pages)
        full_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            full_text += text
            page_metadata = {
                "source": filename,
                "page": i + 1,
                "total_pages": total_pages,
                "file_type": "pdf"
            }
            documents.append(Document(page_content=text, metadata=page_metadata))
            
    # Enforce total char counts on each page-level document metadata
    total_chars = len(full_text)
    for doc in documents:
        doc.metadata["char_count"] = total_chars
        
    return documents

def load_documents(file_paths: List[str]) -> Tuple[List[Document], List[Dict[str, Any]]]:
    """
    Loads all specified files and returns a flat list of all Documents along with stats for each.
    """
    all_documents = []
    file_stats = []
    
    for path in file_paths:
        if not os.path.exists(path):
            file_stats.append({
                "filename": os.path.basename(path),
                "pages": 0,
                "char_count": 0,
                "status": "File not found"
            })
            continue
            
        filename = os.path.basename(path)
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext == ".pdf":
                docs = load_pdf_file(path)
                status = "Success"
            elif ext == ".txt":
                docs = load_text_file(path)
                status = "Success"
            else:
                docs = []
                status = "Unsupported format"
                
            if docs:
                all_documents.extend(docs)
                total_pages = docs[0].metadata.get("total_pages", 1)
                total_chars = docs[0].metadata.get("char_count", 0)
            else:
                total_pages = 0
                total_chars = 0
                
            file_stats.append({
                "filename": filename,
                "pages": total_pages,
                "char_count": total_chars,
                "status": status
            })
        except Exception as e:
            file_stats.append({
                "filename": filename,
                "pages": 0,
                "char_count": 0,
                "status": f"Error: {str(e)}"
            })
            
    return all_documents, file_stats
