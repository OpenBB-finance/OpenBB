---
name: financial_rag_robustness
description: A checklist-driven workflow for testing OpenBB-powered financial RAG and tool-using analyst agents for retrieval, tool-call, grounding, and evaluation failures.
---

# Financial RAG Robustness Checks

Use this guide when an OpenBB MCP workflow, chat assistant, LangGraph graph, or
other tool-using financial agent returns an answer that needs to be trusted,
audited, or debugged. The goal is to turn vague "the agent is wrong" feedback
into a reproducible diagnosis across data retrieval, tool calls, reasoning, and
final reporting.

This skill is intentionally provider-neutral. It does not require a specific
vector database, LLM, or external evaluation framework. It can also be used with
external RAG failure-mode maps by translating each symptom into the OpenBB
checks below.

## When To Use

Run this workflow for:

- filings, news, transcript, or research-note RAG answers
- equity, options, economy, or portfolio workflows that call OpenBB tools
- multi-step analyst agents built with MCP clients, LangGraph, or notebooks
- financial memos where every numeric claim needs a traceable source
- regressions where the same prompt gives inconsistent market or company facts

Do not use it as a substitute for investment, compliance, or legal review. It
only checks whether the AI workflow handled the available data and tools
correctly.

## Robustness Pass

### 1. Freeze The Task

Record the exact:

- user question
- date and timezone
- model or agent version
- active OpenBB tools
- provider names
- input symbols, dates, and filters
- retrieved documents or tool responses, if available

If any item is missing, treat the run as exploratory rather than auditable.

### 2. Classify The Failure

Pick the first matching failure class:

| Class | Symptom | First check |
| --- | --- | --- |
| Retrieval miss | Relevant filing, news item, transcript section, or time series was not used | Query terms, filters, date range, provider coverage |
| Retrieval contamination | Irrelevant company, stale period, or wrong asset leaks into the context | Symbol normalization, CIK/ticker mapping, document metadata |
| Tool-call mismatch | Agent called the wrong OpenBB command or omitted a required provider parameter | Tool schema, active category, generated arguments |
| Numeric hallucination | Answer cites a metric not present in tool output or retrieved text | Result payload, units, transformation, as-of date |
| Temporal leak | Answer uses future data or mixes fiscal/calendar periods | Observation date, filing date, period end, release timestamp |
| Unit or scale error | Basis points, percent, dollars, shares, or split-adjusted prices are mixed | Field metadata, provider docs, chart labels |
| Reasoning gap | Data is correct, but conclusion does not follow | Intermediate calculations, assumptions, thresholds |
| Evaluation blind spot | No check would have caught the wrong answer | Add a deterministic assertion or review rubric |

### 3. Re-run The Data Path Without The Model

Use OpenBB tools directly before blaming the LLM:

1. Call the exact tool the agent should have used.
2. Save or inspect the raw `results`.
3. Confirm the provider and parameter defaults.
4. Check whether the required field exists before transformation.
5. Recompute any derived metric in Python or a notebook.

If the direct OpenBB result is wrong, file a data/provider issue. If the direct
result is correct, continue to the agent checks.

### 4. Check Grounding Claims

For each key sentence in the final answer, attach one of:

- `tool`: the exact OpenBB tool and field
- `document`: source title, section, and date
- `calculation`: formula and input fields
- `assumption`: explicitly marked user or analyst assumption
- `unsupported`: must be removed or reworked

Numeric claims should never be left in the `unsupported` bucket.

### 5. Stress The Retrieval Query

Run at least three query variants:

- narrow: exact ticker, filing period, section, or metric
- broad: company name plus concept
- adversarial: nearby ticker, stale period, or similar metric

The answer should remain stable for narrow and broad queries, and should reject
or clearly disambiguate adversarial queries.

### 6. Stress The Tool Call

For each OpenBB command used by the agent:

- remove optional parameters and observe the defaults
- change provider, if another provider supports the model
- move the date range by one reporting period
- request the same concept through another route when available

If answers change materially, the final memo should disclose provider or period
sensitivity.

### 7. Add Deterministic Evaluation

Convert the failure into at least one assertion:

- the answer must cite the same provider that produced the metric
- every financial value above a threshold must appear in retrieved context
- no observation date can be after the requested analysis date
- the final answer must include `as_of` for market data
- the agent must refuse when symbol disambiguation fails
- the output must include a caveat when provider coverage is incomplete

Prefer deterministic checks over another LLM grader for first-line QA.

## OpenBB Agent QA Template

Use this template in bug reports, PR descriptions, or notebooks:

```text
Question:

Expected answer shape:

OpenBB tools that should be used:

Tool calls actually made:

Provider and as-of dates:

Retrieved documents or result fields:

Unsupported claims:

Failure class:

Deterministic regression check added:
```

## PR Review Checklist For AI Workflows

Before merging an OpenBB MCP, prompt, or agent workflow PR, verify:

- The prompt tells the agent to cite tool outputs, not memory.
- Required tools are activated or discoverable.
- Provider defaults are explicit in examples.
- Time-sensitive claims include an `as_of` date.
- Numeric transformations are implemented in code, not prose.
- The example contains at least one failure or refusal case.
- Tests or docs cover symbol/date/provider ambiguity.

## Example Diagnosis

Symptom: "The analyst agent says Company A's revenue increased 30%, but the
reported financials endpoint shows 3%."

Likely path:

1. Check whether the agent used quarterly or annual data.
2. Check whether values are in units, thousands, or millions.
3. Confirm whether the metric is revenue, operating revenue, or segment revenue.
4. Recompute the growth rate from the exact returned fields.
5. Add a regression check that the final answer must cite the source field names.

Outcome: either fix the provider route, adjust the prompt to require source
field citations, or add a refusal when the route lacks the requested metric.

## Good Final Answer Shape

A robust financial RAG answer should make the provenance visible:

- answer first
- bullet list of cited tool outputs or document sections
- assumptions and exclusions
- sensitivity to provider/date changes
- unsupported items removed or labeled as hypotheses

If the agent cannot produce this shape, keep the output as a draft rather than a
decision-ready memo.
