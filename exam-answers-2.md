# Checkpoint Exam Answers - Part 2

## Section A: LLMOps & MLOps Foundations (8 points)

### Q1 (3 pts)
**Explain the differences between MLOps and LLMOps. Where do they overlap, where do they diverge, and which Module 1 → Module 3 design decisions in your own build map cleanly to one discipline versus the other? Use your own system as the example.**

[Your answer here]
MLOps - entire process from cleaning data to EDA, modeling, deployment, monitoring for machine learning systems ex: regression, classification, forecasting
LLMOps - process from cleaning/data prep to prompt engineering/finetuning/RAG/agent development, to deployment following by monitoring for LLM powered systems: ex customer chat bot, rag system to answer questions about company documents, research agent etc

MLOps
- can involve training model from scratch
- focus on metrics like precision, recall, accuracy etc
- involves experimentation, model versioning, CI/CD
- test data

LLMOps
- uses pre-trained models (API calls or fine-tuning)
- focus on semantic metrics: faithfulness, relevance, hallucination, latency, token cost
- prompt versioning & management (not a thing in traditional ML)
- eval dataset curation (vs labeled testing data)

Tasks to mapping
- chunking strategy - similar to data preprocessing, affects retrieval quality - MLOps
- Hybrid retrieval - ml pattern like ensemble model - MLOps
- prompts for different things ex: llm as a judge - not a thing in ML - LLMOps
- langsmith tracing - LLM specific observability - LLMOps
- Actionability evaluator - LLM as a judge, semantic evaluation - LLM Ops

---

### Q2 (3 pts)
**Walk through the LLM application lifecycle from ideation to operational deployment. For each stage, name one decision a senior engineer makes that a junior engineer would miss.**

PII = Personally Identifiable Information
| Stage | Senior Decision Junior Misses |
|-------|-------------------------------|
| **Ideation** | Define success metrics upfront (latency budget, accuracy threshold) - junior jumps to building |
| **Data sourcing** | Check data licensing/PII before ingesting - junior grabs everything |
| **Preprocessing** | Build validation checks into pipeline (PII detection) - junior does one-off cleaning |
| **Eval dataset** | Build eval set BEFORE building system - junior builds system first, evals later |
| **Prototyping** | Start simple (single retriever) before complex (hybrid) - junior over-engineers |
| **Iteration** | Version everything (prompts, chunks, embeddings) - junior overwrites |
| **Deployment** | Set up tracing/alerts before launch - junior deploys then adds observability |
| **Production** | Build feedback loop into product - junior treats launch as done |
---

### Q3 (2 pts)
**Some LLM apps need full MLOps maturity (CI/CD, registry, lineage, governance). Others can ship with a lighter LLMOps footprint. Give two concrete examples — one of each — and explain what determines which side of the line a system falls on.**

[Your answer here]
Full MLOps needed:
Loan approval system at a bank - regulators require model lineage, audit trails, explainability ("why was this person denied?"), governance for bias testing

Lighter LLMOps sufficient:
CSM RAG - internal tool, human-in-the-loop (CSM reviews before sending to customer), no autonomous decisions, using API calls not training models


Factors:
- who is affected if output is bad -> customer facing vs internal
- regulatory/compliance requirements -> if healthcare/finance vs internal productiivty
- explaiability requirement - does the why for model output matter
- data sensivity - pii, healthcare/financial data vs public data


---

## Section B: Evaluation (12 points)

### Q4 (3 pts)
**Define eval-driven development for LLM applications. How does it differ from test-driven development for traditional software? What changes in your workflow when an evaluator can be wrong, expensive to run, and non-deterministic?**

[Your answer here]
in software, tests are cheap (function calls without LLMS), fast, determinstic output is expected, 100% pass rate is expected, 
in eval driven, api calls so expensive; non determnistic outputs; cant expect 100%, usually some acceptance percent between 60 to 100, evaluator could be wrong (ex LLM as a judge)

What changes when evaluator is wrong/expensive/non-deterministic
- run eval multiple times to see distirbutions not single scores
- need to calirbate (check agreement with humans)
- cant run eval for every small changes, full eval only at milestones


---

### Q5 (3 pts)
**LLM-as-Judge: when is it the right call, when is it the wrong call, and how do you calibrate one so you can trust its output? Describe a concrete calibration procedure you would run on the custom evaluator you built in Part 1.**

[Your answer here]
When to use LLM-as-Judge:
Semantic stuff you can't write a function for - relevance, faithfulness, tone, helpfulness

When NOT to use:
Anything you can check with code (exact match, number lookup, regex)
Domain expertise needed (legal, medical - judge doesn't know better than you)

Calibration procedure for my Actionability evaluator:
Get 30-50 examples, have humans score them
Run my judge on same examples
Compare scores - where does judge disagree with humans?
Tweak the prompt/model until agreement is ~85%+
Spot-check periodically in production to make sure it doesn't drift


---

### Q6 (3 pts)
**Compare algorithmic evaluators, human evaluators, and LLM-as-Judge evaluators across reliability, cost, latency, and what they can measure. Give one example metric that is best measured by each.**

[Your answer here]

Example metrics:
Algorithmic: Retrieval recall@k (did the right doc appear in top k?)
Human: Overall answer quality / user satisfaction
LLM-as-Judge: Faithfulness (is answer grounded in context?)


Algorithmic:

Cost: Low (just compute)
Latency: Very low (milliseconds)
Reliability: Perfect (deterministic, same input → same output)
Measures: Exact/computable things
Example: Retrieval recall@k
Human:

Cost: High ($$$/hour)
Latency: Very high (hours/days to schedule)
Reliability: Medium (humans disagree, get tired)
Measures: Anything, including nuance and edge cases
Example: Overall answer quality / user satisfaction
LLM-as-Judge:

Cost: Medium (API calls)
Latency: Low (seconds)
Reliability: Medium-low (non-deterministic, needs calibration)
Measures: Semantic qualities at scale
Example: Faithfulness
---

### Q7 (3 pts)
**Evaluating a multi-step agent is meaningfully harder than evaluating a single-shot RAG. Name three specific failure modes that show up in agents but not in your Module 1 RAG, and explain how you would catch each with Arize-style agent evaluation.**

[Your answer here]
Agent-specific failure modes (not in RAG):

Wrong plan / bad reasoning
Agent decides to do steps in wrong order or picks wrong approach
Catch: LLM-as-Judge on the plan/trajectory

Tool selection errors
Called search when should have called calculator
Catch: Compare tool calls to expected in eval set

Tool argument errors
Right tool, wrong inputs (searched wrong query)
Catch: Compare arguments to expected

Looping / getting stuck
Agent repeats same action, never terminates
Catch: Max steps limit, loop detection in traces
Error recovery failure

Tool returns error, agent doesn't adapt
Catch: Trace analysis - did it retry with different approach?
State/context loss across steps

Agent "forgets" info from earlier steps
Catch: Check if final answer uses info from all relevant steps

What Arize-style tracing catches:

Full trajectory visualization (see each step)
Latency per step (where is it slow?)
Token usage accumulation
Tool call success/failure rates
Span-level evaluation (judge each step, not just final output)

---

## Section C: Observability & Monitoring (10 points)

### Q8 (3 pts)
**Distinguish tracing, logging, and metrics. For your Module 3 build, give one concrete example of each — what specific signal you capture, in which tool, and what production question that signal lets you answer that the other two cannot.**

[Your answer here]
Tracing:

The full journey of ONE request through your system
Shows: Query → Embedding (50ms) → Pinecone (120ms) → BM25 (30ms) → LLM (800ms) → Response
Answers: "Why was THIS specific request slow?" or "What context did THIS query retrieve?"
Tool: LangSmith, Phoenix

Logging:

Individual events/records as they happen
Examples: [INFO] User query received, [ERROR] Pinecone timeout, [WARN] Low confidence response
Answers: "What errors happened today?" or "How many timeouts this week?"
Tool: stdout

Metrics:
performance measurement over time
ex: p95 latency, avg faithfulness, requests/min
Tool: Phoenix stats

---

### Q9 (4 pts)
**List four production failure modes for a deployed RAG system that you would only catch with proper observability — i.e., that would not show up in a passing eval run. For each: the metric, the threshold, the alert action, and which observability tool surfaces it.**

[Your answer here]
Latency spike
metric p95 latency
threshold > 3s
alert: check open ai and pinecone status
tool: LangSmith

Retrieval returning empty/few results
Metric: avg docs retrieved per query
Threshold: <2 docs (normally get 5)
Alert: Check if index is healthy, embedding model changed
Tool: LangSmith

Error rate spike
Metric: % of requests returning error (OpenAI timeout, Pinecone down)
Threshold: >1% errors
Alert: Check API status, rate limits
Tool: Logs + metrics dashboard

Token usage explosion
Metric: avg tokens per request
Threshold: >2x normal (e.g., >4000 when usually 2000)
Alert: Check if retrieval is pulling too much context, cost alert
Tool: LangSmith/Phoenix token tracking

RAG Confidence score drop (if your RAG outputs confidence)
Metric: avg confidence score
Threshold: drops below 0.6
Alert: Corpus may be stale, queries shifting
Tool: Custom logging of your RAGResponse.confidence

---

### Q10 (3 pts)
**Distinguish data drift, concept drift, and prompt drift in an LLM application. For each, give a realistic scenario in your CSM RAG context, the signal that would let you detect it in monitoring, and one mitigation.**

[Your answer here]
Data drift - input disitbrutuon change
ex: new product quesions
detection - low retieval scores, new query patterns

concept drift - ground truth change
ex: documents change -> for example policy change
detection: user complaints human review

prompt drifts - prompt or model behavior changes
model like gpt 4 is upgraded or you iterate system prompt across iteration which fixes some issue but makes other issues worse; eval scores trending down

---

## Section D: Data Quality (10 points)

### Q11 (4 pts)
**Walk through the data quality dimensions (completeness, accuracy, consistency, timeliness, validity, uniqueness) and explain which apply to a RAG corpus, which apply to retrieval results, and which apply to generation outputs. For three of those dimensions, write the Great Expectations expectation you would author and what failure it would catch.**

[Your answer here]
completeness
CORPUS: data should be complete (chunks have metadata) - catch chunks ingested without proper metadata
Retrieval: retrieved enough docs to answer
Generation: fully answer question using relevant docs

Accuracy
Corpus: has accurate info to answer questions
Retrieved: docs are relevant to query
accuracy: answer is faithful to context

Consistency:
corpus: Docs don't contradict each other
retrieval: etrieved docs agree with each other
generation: answer doesnt contradict itself

Timeliness:
Corpus: Data is up-to-date
retrieval: n/a (or maybe low latency)
generation: n/a (or maybe low latency)

Validity
Corpus: valid documents only, are documents that become invalid over time, outdated etc should be removed; chunks are correct size
retrieval: N/A
generation: Output matches expected schema

Uniqueness:
Corpus: no duplicate chunks
retrieval: Retrieved docs aren't duplicates
generation: N/A

---

### Q12 (3 pts)
**You discover your CSM RAG occasionally surfaces customer PII from old support tickets in its retrieved context. Walk through how you would (a) detect this in your existing data quality suite, (b) prevent it from reaching generation, (c) prevent it from re-entering the corpus on the next ingestion run.**


[Your answer here]
(a) Detect in existing data quality suite:
Run PII regex patterns on all chunks (you already built this in expect_no_pii())
Flags chunks containing emails, phones, SSNs
Your run found 10 chunks with emails

(b) Prevent from reaching generation:
Option 1: Filter out PII-flagged chunks at retrieval time
Option 2: Redact PII in retrieved context before passing to LLM
Option 3: Post-process LLM output to catch any leaks (last resort)

(c) Prevent re-entering on next ingestion:
Add redaction step BEFORE chunking in ingestion pipeline
raw_text → redact_pii(text) → chunk → embed → index
"Raghav 555-123-4567" → "[NAME] [PHONE]" before it ever becomes a chunk


---

### Q13 (3 pts)
**The corpus you indexed in Module 1 will not be the corpus you serve in month six. Describe a corpus change validation strategy: what you check on every ingestion, what you check weekly, what you check before promoting an updated index to production. Be specific about the expectations that gate each step.**

[Your answer here]

Every ingestion:
- expect_no_pii() passes
- expect_chunk_length_in_range(100, 1500)
- expect_metadata_complete()
- expect_no_duplicates()
- gate: All pass or block ingestion

Weekly:
- Corpus size within expected range (±10%)
- Doc type distribution stable
- No docs older than staleness threshold
- Gate: Investigate anomalies before next ingestion

Before production promotion:
- Full eval suite (faithfulness ≥0.9, relevance ≥0.9, actionability ≥0.5)
- Latency p95 ≤2s
- Compare to current prod scores
→ Gate: New index ≥ current index on all metrics

Promotion frequency: Weekly, or on-demand when critical docs update
---
