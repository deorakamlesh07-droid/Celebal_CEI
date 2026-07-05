"""
Text Preprocessing Module.
Cleans raw text data and normalizes whitespace.
"""

import re
from typing import List
from langchain_core.documents import Document

def clean_text(text: str) -> str:
    """
    Cleans raw text by normalizing whitespace and removing non-printable characters.
    """
    if not text:
        return ""
    # Standardize multiple spaces and tabs to a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Filter out non-printable characters, maintaining standard linebreaks and tabs
    text = "".join(ch for ch in text if ch.isprintable() or ch in "\n\r\t")
    # Strip whitespace from each line and remove empty lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned = "\n".join(line for line in lines if line)
    return cleaned.strip()

def preprocess_documents(documents: List[Document]) -> List[Document]:
    """
    Applies text cleaning to a list of LangChain Documents and returns the preprocessed list.
    """
    preprocessed_docs = []
    for doc in documents:
        cleaned_content = clean_text(doc.page_content)
        new_doc = Document(
            page_content=cleaned_content,
            metadata=doc.metadata.copy()
        )
        preprocessed_docs.append(new_doc)
    return preprocessed_docs
