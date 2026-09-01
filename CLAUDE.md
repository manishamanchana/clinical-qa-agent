# Guideline-Grounded Clinical Q&A Agent

Portfolio project for UAB outreach (first in sequence — targets DBIDS,
John Osborne / Abu Mosa, LLM/NLP fit). Scoped in
`~/projects/second-brain/second-brain/raw/UAB_outreach.md`. Deliverable:
a running demo repo (not a description) to attach directly in outreach
emails.

This is a code repo, not a knowledge-base vault. Session notes/decisions
get dropped into `~/projects/second-brain/second-brain/raw/` for ingest
into the wiki — don't duplicate tracking here.

## What it does
RAG agent over public CDC/WHO clinical guideline PDFs. Answers questions
with inline source citations; declines to answer when retrieval confidence
is low. Informational only — no diagnostic/treatment advice, must not be
framed as a deployable clinical tool.

## Stack
Python, LangChain, FAISS (vector store), Ollama (local LLM), Streamlit,
Docker for packaging.

Note: original scoping doc specifies AWS Bedrock as the LLM (see quote
below). Switched to Ollama (2026-08-31) to avoid AWS account/billing
setup — decision doesn't affect outreach fit since Osborne/Mosa's
interest is LLM/NLP/predictive modeling generally, not the specific
cloud vendor. Swappable back to Bedrock later via `langchain-aws`
(already in requirements.txt) if desired — see PLAN.md.

## Deliverable (target: 2–3 days)
A containerized app/notebook that ingests a small guideline corpus,
answers questions with inline citations, and includes a guardrail that
declines unsupported questions.

See `PLAN.md` for the day-by-day breakdown.

## Original project idea (verbatim, from `UAB_outreach.md`)

> **Project 3 (AI agent): Guideline-Grounded Clinical Q&A Agent**
> - Description: A retrieval-augmented agent that answers questions over
>   public clinical/public-health guideline documents and returns
>   citation-grounded passages, refusing to answer when retrieval
>   confidence is low (informational only, no diagnostic/treatment
>   advice).
> - Dataset: Public CDC/WHO guideline PDFs and/or MIMIC-IV / PhysioNet
>   open dataset documentation.
> - Tech stack: Python, LangChain, FAISS (vector store), AWS Bedrock
>   (LLM), Streamlit; Docker for packaging.
> - 2–3 day deliverable: A containerized app/notebook that ingests a small
>   guideline corpus, answers questions with inline source citations, and
>   includes a guardrail that declines unsupported questions.

Outreach framing (from the same doc): lead with Osborne or Mosa
(LLM/NLP/predictive modeling), attach the running demo repo link, not a
description. Caveat: public/synthetic data only, explicitly a
demonstration — must not be framed as diagnostic, treatment, or a
deployable clinical tool.
