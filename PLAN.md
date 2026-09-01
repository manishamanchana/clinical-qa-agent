# Plan — Guideline-Grounded Clinical Q&A Agent

Scoped 2026-08-30. Target: 2–3 focused days.

## Day 1 — Corpus + retrieval
- Install Ollama and pull a local model (e.g. `llama3` or `mistral`) —
  switched from AWS Bedrock (2026-08-31) to avoid AWS account/billing
  setup; see CLAUDE.md Stack note. Swappable back to Bedrock later via
  `langchain-aws` if desired.
- Topic: **adult hypertension screening and management** (2026-08-31).
  Corpus is these three documents, saved into `data/raw/`:
  1. WHO "Guideline for the pharmacological treatment of hypertension in
     adults" (2021) — WHO IRIS PDF:
     https://iris.who.int/server/api/core/bitstreams/f062769d-f075-4a00-87af-0a2106e0bd04/content
     (also on NCBI Bookshelf as NBK573631)
  2. USPSTF "Screening for Hypertension in Adults" 2021 reaffirmation
     (Grade A):
     https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/hypertension-in-adults-screening
  3. (Optional, if time) CDC Million Hearts "Hypertension Control Change
     Package," 2nd ed.: https://stacks.cdc.gov/view/cdc/251804
- Chunk + embed the corpus, build a FAISS index.
  - Each chunk needs metadata: source title, publisher, source URL, page
    number — so answers can cite the exact source + page.
  - Use PyPDFLoader's `page_label` field for the cited page number, not
    the raw 0-indexed `page` field (decided 2026-08-31) — `page_label`
    reflects the document's own printed page numbering (e.g. WHO PDF's
    front matter uses letters like `'a'` before switching to numerals),
    so it matches what a reader actually sees on the page.
  - The WHO doc has numbered recommendations (sections 3.1–3.8) — keep
    each numbered recommendation intact within a single chunk rather
    than splitting mid-recommendation.
  - Known limitation (2026-09-01): `PyPDFLoader` loads one `Document` per
    PDF page, and the text splitter chunks each page independently, so it
    never merges content across a page boundary. A recommendation that
    lives entirely on one page stays in one chunk; a recommendation that
    spans multiple pages (e.g. 3.1, which continues from page 18 into
    page 19) still ends up split across chunks at the page boundary,
    regardless of `chunk_size`. Chose `chunk_size=4000` (based on
    inspecting actual WHO recommendation-page lengths, ~1600–4000 chars)
    to avoid *extra* splits within a page, which is as far as this
    mitigates the issue without reworking ingestion to merge pages.

## Day 2 — RAG chain + guardrail
- Retrieval → Ollama LLM call → citation-formatted answer.
- Decide and implement the "decline if low retrieval confidence" guardrail
  — needs a similarity-score threshold; pick one empirically by testing
  against a few known-answerable and known-unanswerable questions.
- Guardrail scope (2026-08-31): decline questions about hypertensive
  emergencies/urgencies, drug dosing specifics, and secondary/resistant
  hypertension — WHO's guideline explicitly excludes these topics — plus
  anything else not covered by the corpus.

## Day 3 — Packaging + polish
- Streamlit wrapper (or CLI, whichever is faster to finish cleanly).
- Dockerize.
- README: what it does, how to run it, example Q&A including one that
  triggers the decline guardrail (shows the safety behavior works, not
  just the happy path).
- Push to GitHub, link goes in the Osborne/Mosa outreach email.

## Risks
- Local machine resource limits (RAM/disk for the Ollama model download
  and inference) are the most likely Day-1 blocker — check this first,
  before building anything else.
- Guideline PDF parsing quality (tables, multi-column layouts) can eat
  time — keep the initial corpus simple (text-heavy guidelines) rather
  than fighting PDF layout parsing under time pressure.
