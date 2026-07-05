"""
Vector Database Store Module.
Manages creation, serialization, loading, and file size statistics of the FAISS vector store.
"""

import os
from typing import List, Optional, Dict, Any
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

DEFAULT_STORE_DIR = os.path.join("data", "vector_store")
FAISS_INDEX_NAME = "index"

def get_db_path(base_dir: str = DEFAULT_STORE_DIR) -> str:
    """
    Returns the storage directory path.
    """
    return base_dir

def build_vector_store(
    chunks: List[Document], 
    embeddings: Embeddings,
    store_dir: str = DEFAULT_STORE_DIR
) -> FAISS:
    """
    Creates a FAISS vector store from document chunks and saves it locally.
    """
    if not os.path.exists(store_dir):
        os.makedirs(store_dir)
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(store_dir, index_name=FAISS_INDEX_NAME)
    return db

def load_vector_store(
    embeddings: Embeddings,
    store_dir: str = DEFAULT_STORE_DIR
) -> Optional[FAISS]:
    """
    Loads a FAISS vector store index from the local storage directory.
    """
    index_file = os.path.join(store_dir, f"{FAISS_INDEX_NAME}.faiss")
    if not os.path.exists(index_file):
        return None
    return FAISS.load_local(
        folder_path=store_dir,
        embeddings=embeddings,
        index_name=FAISS_INDEX_NAME,
        allow_dangerous_deserialization=True
    )

def get_vector_store_stats(store_dir: str = DEFAULT_STORE_DIR) -> Dict[str, Any]:
    """
    Calculates storage metrics (file existence, bytes, format size) of the FAISS index.
    """
    index_file = os.path.join(store_dir, f"{FAISS_INDEX_NAME}.faiss")
    pkl_file = os.path.join(store_dir, f"{FAISS_INDEX_NAME}.pkl")
    
    if not os.path.exists(index_file):
        return {
            "exists": False,
            "storage_path": store_dir,
            "total_bytes": 0,
            "formatted_size": "0 KB"
        }
        
    total_bytes = 0
    for file_path in [index_file, pkl_file]:
        if os.path.exists(file_path):
            total_bytes += os.path.getsize(file_path)
            
    if total_bytes < 1024 * 1024:
        formatted_size = f"{total_bytes / 1024:.2f} KB"
    else:
        formatted_size = f"{total_bytes / (1024 * 1024):.2f} MB"
        
    return {
        "exists": True,
        "storage_path": os.path.abspath(store_dir),
        "total_bytes": total_bytes,
        "formatted_size": formatted_size
    }
