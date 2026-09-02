"""RAG chain + guardrails, extracted from notebooks/02_qa_chain.ipynb (Day 2).

The notebook stays as the piece-by-piece dev artifact; this module is the
shippable version the Streamlit app (and anything else) imports from.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS

# Configurable via env so the same code runs unchanged whether Ollama is on
# localhost (local dev) or reached from inside a Docker container.
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"
INDEX_PATH = Path(__file__).resolve().parent.parent / "data" / "faiss_index"

# Picked empirically (2026-09-01, see PLAN.md): answerable-question top-1
# FAISS L2 distances landed at 196-276, unanswerable ones at 368+.
CONFIDENCE_THRESHOLD = 320.0

ANSWER_PROMPT = """You are a clinical guideline assistant. Answer the question \
using ONLY the context below, which is excerpted from public CDC/WHO/USPSTF \
hypertension guidelines. Do not use outside knowledge. If the context does not \
contain enough information to answer, say so plainly instead of guessing.

This is informational only — not diagnostic or treatment advice for any
individual patient.

Context:
{context}

Question: {question}

Answer:"""

DECLINE_LOW_CONFIDENCE = (
    "I don't have enough information in the corpus (WHO pharmacological "
    "hypertension guideline, USPSTF screening recommendation, and CDC Million "
    "Hearts change package) to answer that confidently. This tool only covers "
    "adult hypertension screening and management, and is informational only "
    "— not diagnostic or treatment advice."
)

# Keyword patterns for the three excluded topics (2026-08-31 scope decision).
# "Drug dosing specifics" requires a digit before "mg" (an actual dose
# amount) rather than matching bare "mg" — bare "mg" false-positived on
# in-scope questions like sodium intake, a dietary unit the CDC corpus does
# cover (caught during Day 2 testing).
SCOPE_EXCLUSIONS = {
    "hypertensive emergency/urgency": re.compile(
        r"hypertensive (emergenc|urgenc)|\bmalignant hypertension\b", re.I
    ),
    "drug dosing specifics": re.compile(
        r"\bdos(e|age|ing)\b|\d+\s*mg\b|\bmilligram", re.I
    ),
    "secondary/resistant hypertension": re.compile(
        r"secondary hypertension|resistant hypertension", re.I
    ),
}


@dataclass
class QAResult:
    answer: str
    citations: list[str] = field(default_factory=list)
    declined: bool = False
    decline_reason: str | None = None  # "scope" | "confidence" | None


_vectorstore = None
_llm = None


def get_vectorstore() -> FAISS:
    """Lazily loaded + cached so importing this module doesn't require Ollama
    to be reachable (useful for tests / static analysis)."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)
        _vectorstore = FAISS.load_local(
            str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True
        )
    return _vectorstore


def get_llm() -> Ollama:
    global _llm
    if _llm is None:
        _llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    return _llm


def retrieve(question: str, k: int = 4):
    """Top-k (Document, score) pairs; lower score = more similar (FAISS L2 distance)."""
    return get_vectorstore().similarity_search_with_score(question, k=k)


def generate_answer(question: str, retrieved) -> str:
    context = "\n\n---\n\n".join(doc.page_content for doc, _ in retrieved)
    prompt = ANSWER_PROMPT.format(context=context, question=question)
    return get_llm().invoke(prompt)


def format_citations(retrieved) -> list[str]:
    seen = []
    for doc, _ in retrieved:
        m = doc.metadata
        entry = f"{m['title']} ({m['publisher']}), p. {m['page_label']}"
        if entry not in seen:
            seen.append(entry)
    return seen


def is_low_confidence(retrieved, threshold: float = CONFIDENCE_THRESHOLD) -> bool:
    top_score = retrieved[0][1]
    return top_score > threshold


def out_of_scope_topic(question: str) -> str | None:
    """Returns the matched exclusion label, or None if in scope."""
    for label, pattern in SCOPE_EXCLUSIONS.items():
        if pattern.search(question):
            return label
    return None


def decline_scope_message(label: str) -> str:
    return (
        f"This question touches on {label}, which the underlying WHO "
        "guideline explicitly excludes from its scope, so this tool declines "
        "to answer it. This is informational only — not diagnostic or "
        "treatment advice."
    )


def ask(question: str, k: int = 4) -> QAResult:
    """Scope check first (cheapest, catches things confidence can't), then
    retrieval + confidence check, then — only if both pass — the LLM call."""
    scope_hit = out_of_scope_topic(question)
    if scope_hit:
        return QAResult(
            answer=decline_scope_message(scope_hit),
            declined=True,
            decline_reason="scope",
        )

    retrieved = retrieve(question, k=k)
    if is_low_confidence(retrieved):
        return QAResult(
            answer=DECLINE_LOW_CONFIDENCE, declined=True, decline_reason="confidence"
        )

    answer = generate_answer(question, retrieved)
    citations = format_citations(retrieved)
    return QAResult(answer=answer, citations=citations)
