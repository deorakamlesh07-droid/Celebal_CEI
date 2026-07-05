"""
Answer Generation Module.
Manages ChatGroq model connections and generates responses using either simple or improved prompt configurations.
"""

import os
import time
from typing import Tuple, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Strict system prompts as requested
SIMPLE_PROMPT = """You are a helpful AI assistant.
Answer ONLY from the provided context.
If the answer is not available, reply "I could not find this information in the uploaded document."
Never hallucinate.

Context:
{context}

Question:
{question}

Answer:"""

# Improved prompt comparison design (structured response, formatting instruction)
IMPROVED_PROMPT = """You are an expert AI assistant that answers questions using ONLY the provided context.

[INSTRUCTIONS]
1. Answer the question comprehensively and clearly based STRICTLY on the given context.
2. If the context does not contain the answer, reply EXACTLY with: "I could not find this information in the uploaded document."
3. Do not assume, extrapolate, or hallucinate any facts.
4. Structure the response using clean formatting (bullet points or bold text) for readability where appropriate.

Context:
{context}

Question:
{question}

Answer:"""

def get_llm(model_name: Optional[str] = None) -> ChatGroq:
    """
    Instantiates and returns the ChatGroq model using the API key in the environment.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set. Please add it to your .env file or environment.")
    
    model = model_name or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    return ChatGroq(model=model, temperature=0.1)

def generate_answer(
    question: str, 
    context: str, 
    prompt_type: str = "Simple", 
    model_name: Optional[str] = None
) -> Tuple[str, float]:
    """
    Generates an answer using the chosen prompt template and Groq model.
    Returns:
    1. Generated text response
    2. Inference latency (seconds)
    """
    llm = get_llm(model_name)
    
    template_str = SIMPLE_PROMPT if prompt_type == "Simple" else IMPROVED_PROMPT
    prompt_template = ChatPromptTemplate.from_template(template_str)
    
    chain = prompt_template | llm
    
    start_time = time.time()
    response = chain.invoke({"question": question, "context": context})
    latency = time.time() - start_time
    
    return response.content, latency
