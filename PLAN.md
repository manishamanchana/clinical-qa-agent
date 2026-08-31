# Plan — Guideline-Grounded Clinical Q&A Agent

Scoped 2026-08-30. Target: 2–3 focused days.

## Day 1 — Corpus + retrieval
- Confirm AWS Bedrock access/credentials work (studies.md lists Bedrock in
  the existing tech stack, so likely already set up — verify, don't
  assume).
- Gather 5–10 public CDC/WHO guideline PDFs (pick a narrow topic so the
  corpus is coherent, not a random grab-bag).
- Chunk + embed the corpus, build a FAISS index.

## Day 2 — RAG chain + guardrail
- Retrieval → Bedrock LLM call → citation-formatted answer.
- Decide and implement the "decline if low retrieval confidence" guardrail
  — needs a similarity-score threshold; pick one empirically by testing
  against a few known-answerable and known-unanswerable questions.

## Day 3 — Packaging + polish
- Streamlit wrapper (or CLI, whichever is faster to finish cleanly).
- Dockerize.
- README: what it does, how to run it, example Q&A including one that
  triggers the decline guardrail (shows the safety behavior works, not
  just the happy path).
- Push to GitHub, link goes in the Osborne/Mosa outreach email.

## Risks
- Bedrock access/quota issues are the most likely Day-1 blocker — check
  this first, before building anything else.
- Guideline PDF parsing quality (tables, multi-column layouts) can eat
  time — keep the initial corpus simple (text-heavy guidelines) rather
  than fighting PDF layout parsing under time pressure.
