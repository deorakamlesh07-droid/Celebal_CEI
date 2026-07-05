"""
System Metrics and Validation Module.
Tracks pipeline latencies and provides an automated test suite verifying groundedness on five sample questions.
"""

import time
from typing import List, Dict, Any
from langchain_community.vectorstores import FAISS
from modules.retriever import retrieve_documents
from modules.generator import generate_answer

DEFAULT_VALIDATION_QUESTIONS = [
    "What is the primary topic or goal of this document?",
    "Are there any specific dates, deadlines, or milestones listed?",
    "Who are the key people, organizations, or authors mentioned?",
    "Summarize the main findings or summary points of the text.",
    "What limitations, requirements, or next steps are described?"
]

def run_system_validation(
    vector_store: FAISS,
    questions: List[str] = None,
    prompt_type: str = "Simple"
) -> List[Dict[str, Any]]:
    """
    Runs automated validation tests on five sample questions.
    Checks if context was retrieved and verifies answers are grounded (no hallucination).
    """
    if not questions:
        questions = DEFAULT_VALIDATION_QUESTIONS[:5]
        
    validation_results = []
    
    for idx, question in enumerate(questions, 1):
        try:
            # 1. Retrieval Latency
            start_retrieval = time.time()
            retrieved_records = retrieve_documents(vector_store, question, k=3)
            retrieval_time = time.time() - start_retrieval
            
            # Combine text content for generation context
            context_text = "\n\n".join([doc["content"] for doc in retrieved_records])
            
            # 2. Generation Latency
            start_gen = time.time()
            if context_text.strip():
                answer, gen_time = generate_answer(
                    question=question, 
                    context=context_text, 
                    prompt_type=prompt_type
                )
            else:
                answer = "I could not find this information in the uploaded document."
                gen_time = 0.0
                
            total_time = retrieval_time + gen_time
            
            # 3. Groundedness validation checks
            status = "PASS"
            failure_reason = ""
            
            if not retrieved_records:
                status = "FAIL"
                failure_reason = "No context chunks retrieved from index."
            elif not answer.strip():
                status = "FAIL"
                failure_reason = "Null or empty response returned."
            elif "I could not find this information" in answer:
                status = "PASS"
                failure_reason = "Correct grounded refusal (no relevant context)."
            else:
                # Basic groundedness heuristic: check overlap of important words
                stop_words = {"the", "a", "an", "is", "are", "of", "and", "in", "to", "for", "on", "with", "this", "that", "it"}
                answer_words = [w.strip(".,;:?!'\"()").lower() for w in answer.split() if w.strip(".,;:?!'\"()").lower() not in stop_words]
                
                matches = [w in context_text.lower() for w in answer_words if len(w) > 3]
                if matches:
                    match_ratio = sum(matches) / len(matches)
                    # If less than 25% of words generated match context, flag possible hallucination
                    if match_ratio < 0.25:
                        status = "FAIL"
                        failure_reason = f"Potential hallucination detected (Grounded ratio: {match_ratio:.1%})."
                else:
                    pass
                    
            validation_results.append({
                "id": idx,
                "question": question,
                "answer": answer,
                "retrieved_chunks": retrieved_records,
                "status": status,
                "reason": failure_reason,
                "latency_sec": total_time
            })
            
        except Exception as e:
            validation_results.append({
                "id": idx,
                "question": question,
                "answer": f"Error: {str(e)}",
                "retrieved_chunks": [],
                "status": "FAIL",
                "reason": f"System crash: {str(e)}",
                "latency_sec": 0.0
            })
            
    return validation_results
