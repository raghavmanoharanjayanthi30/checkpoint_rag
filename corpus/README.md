# Helix Corpus — Module 1 Checkpoint

This is the corpus for the **AiEngineerAccelerator™ Module 1 (LLMs & RAG) Checkpoint Build**. You will ingest these documents into your RAG system and evaluate against the included test set.

The corpus is the entire fictional knowledge base of **Helix**, a B2B SaaS workflow automation platform. Helix doesn't exist outside of this corpus — every fact, plan, integration, error code, and policy is defined within these files. This means your test queries have unambiguous ground-truth answers.

## Structure

```
corpus/
├── README.md                  ← you are here
├── test_set.json              ← 50 evaluation queries with ground truth
├── product-docs/              ← 60 markdown files
│   ├── getting-started/       (5)
│   ├── workflows/             (10)
│   ├── integrations/          (10)
│   ├── api/                   (10)
│   ├── admin/                 (8)
│   ├── billing/               (5)
│   ├── data/                  (6)
│   ├── notifications/         (4)
│   └── mobile/                (2)
├── runbooks/                  ← 25 PDFs (5 scanned, 20 text-native)
│   ├── incident-response/     (5)
│   ├── customer-ops/          (9)
│   ├── engineering/           (5)
│   └── csm/                   (6)
└── tickets/                   ← 15 HTML resolved support tickets
```

**File counts:** 60 markdown + 25 PDF + 15 HTML = **100 documents total.**

## What makes this corpus realistic

This isn't a clean academic dataset. It mirrors what you'd actually find inside a SaaS company's internal knowledge base:

- **Multiple file formats** — markdown for docs, PDF for runbooks, HTML for tickets. Your ingestion pipeline needs to handle each appropriately.
- **Scanned PDFs** — 5 of the runbooks are image-based (no text layer). Either OCR them or fail gracefully — both are valid engineering decisions, but they need to be conscious decisions.
- **Cross-referenced facts** — the same fact (e.g., 30-minute workflow timeout) is mentioned across multiple docs. Good retrieval should consolidate these.
- **Tables, code blocks, structured lists** — your chunker will need to handle these without mangling them.
- **Realistic conversation structure in tickets** — multiple turns, with the resolution often appearing only in the final agent response.
- **Some facts only in tickets** — certain edge cases are documented only in resolved tickets (not in the formal product docs). Good retrieval surfaces tickets when they're the best source.
- **Some facts only in runbooks** — incident procedures and CSM playbooks aren't in product docs. CSM-facing queries often need runbook context.

## Test Set (`test_set.json`)

50 queries split:

| Difficulty | Count | What they test |
|------------|-------|----------------|
| Easy       | 20    | Single-doc, direct factual answers |
| Medium     | 20    | Multi-doc synthesis, scenario-based, specific details |
| Hard       | 10    | Cross-corpus synthesis (e.g., runbook + ticket + product doc), edge cases |

Each query has:

- `id` — stable identifier (Q001, Q002, ...)
- `query` — the user-facing question
- `ground_truth_answer` — canonical answer derived from the corpus
- `expected_sources` — list of corpus paths that should be retrieved to answer
- `difficulty` — easy / medium / hard
- `category` — domain area (api, workflows, billing, admin, etc.)
- `notes` — what counts as a correct answer (for SME review and automated scoring)

### Recommended evaluation metrics

- **Context Precision** — of the chunks your retrieval surfaced, how many came from `expected_sources`?
- **Context Recall** — of the `expected_sources`, how many had at least one chunk surfaced?
- **Faithfulness** — does your generated answer actually derive from the retrieved context, or is it hallucinated?
- **Answer Correctness** — does your answer match the ground truth on the specific facts called out in `notes`?

### Pass thresholds

The Module 1 checkpoint requires:

- Faithfulness ≥ 0.70 across all 50 queries
- Context Precision ≥ 0.60 across all 50 queries
- All automated tests must pass

These are floors, not ceilings. Higher numbers are better and demonstrate stronger engineering judgment in retrieval design.

## How to use

1. Ingest everything under `product-docs/`, `runbooks/`, and `tickets/` into your vector store.
2. Build your retrieval and generation pipeline (covered in Units 1.5–1.7 of the curriculum).
3. Run your eval harness against `test_set.json`.
4. Report metrics in your `eval-report.md`.

You should NOT use the contents of `test_set.json` to influence retrieval at runtime — that defeats the point of the eval. Use it only to score your pipeline.

## Important notes

- **All facts in this corpus are fictional.** Helix is not a real company. Don't try to look up Helix online; everything you need is in these files.
- **Some PDFs are deliberately scanned** (image-only, no text layer). Your pipeline should handle this — either via OCR or by gracefully skipping unreadable PDFs. Don't crash on them.
- **The corpus is internally consistent.** If your system gives an answer that contradicts another part of the corpus, that's a retrieval or generation problem, not a corpus bug.

— BASWE / AiEngineerAccelerator™
