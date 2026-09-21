# Taama Claim Checker

A deterministic claim compliance checker for the Australia market, built for the Taama Developer Take-Home Assignment.

The implementation prioritizes **correctness, traceability, repeatability, and explicit uncertainty** over UI polish or broad but unreliable coverage.

## What it does

The checker:

1. Reads raw-text product claims.
2. Evaluates each claim against a scoped deterministic Australia rule set.
3. Applies the relevant FSANZ or TGA context.
4. Returns:
   - Green / Amber / Red verdict
   - rule ID
   - regulatory authority
   - plain-English justification
   - traceable source document / section / excerpt
5. Falls back to **Amber / NEEDS REVIEW** when a sufficiently reliable rule is not available.

No LLM is used in the decision path.

## Scope

Implemented:

- Australia market
- FSANZ and TGA regulatory contexts
- raw-text claim input
- deterministic rule evaluation
- exact / contains / keyword matching modes
- Green / Amber / Red verdicts
- traceable regulatory references
- conservative unknown-claim handling
- benchmark validation against all three supplied products
- two consecutive result runs per product
- Docker / Docker Compose workflow
- FastAPI health endpoint
- Pytest regression suite

Deliberately skipped:

- image extraction
- PDF extraction
- webpage extraction
- OCR
- LLM / RAG-based verdict generation
- full Australian regulatory corpus coverage
- graphical UI

Those were skipped so the limited implementation time could be spent on verdict correctness and auditability.

## Sample-bank result

Current benchmark against the provided case-study ground truth:

| Product | Correct |
| --- | ---: |
| Comvita Kids Herbal Syrup | 19 / 19 |
| Arepa Brain Drink | 23 / 23 |
| Seed AM-02 Energy + Focus | 29 / 29 |
| **Total** | **71 / 71** |

This is **100% accuracy on the provided sample bank only**. It should not be interpreted as 100% coverage or accuracy across Australian regulation generally.

## Requirements

The easiest path is Docker.

Required:

- Docker
- Docker Compose
- Make

For local Python execution:

- Python 3.12
- dependencies from `requirements.txt`

No API keys or external services are required.

## Run with Docker

Build and start:

```bash
make up
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"status":"healthy"}
```

Run tests:

```bash
make test
```

Stop:

```bash
make down
```

## Run locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Run the sample-bank benchmark:

```bash
python scripts/benchmark_ground_truth.py
```

Generate the committed two-run result files:

```bash
python scripts/generate_results.py
```

## Raw-text inputs

The three case-study inputs are stored in:

```text
inputs/
├── comvita_kids_herbal_syrup.txt
├── arepa_brain_drink.txt
└── seed_am_02.txt
```

Each non-empty line is treated as one claim.

## Results

Generated result files are stored in:

```text
results/
├── comvita_kids_herbal_syrup.json
├── arepa_brain_drink.json
└── seed_am_02.json
```

Each file contains **two consecutive runs**.

The `stable` field confirms whether both runs are identical.

Each matched claim contains:

```json
{
  "claim": "...",
  "verdict": "green",
  "status": "matched_rule",
  "reason": "...",
  "rule_id": "AU-...",
  "authority": "TGA",
  "claim_type": "...",
  "source": {
    "document": "Sources & Logic - AUS.docx",
    "section": "...",
    "page": null,
    "excerpt": "..."
  }
}
```

## Architecture

```text
raw text
   |
   v
normalization
   |
   v
regulatory context
(FSANZ / TGA)
   |
   v
deterministic rule matching
   |
   +--> matched rule
   |      |
   |      v
   |   Green / Amber / Red
   |   + traceable source
   |
   +--> no reliable match
          |
          v
       Amber
       NEEDS REVIEW
```

Core files:

```text
src/models.py      domain models
src/rules.py       regulatory rule loading
src/checker.py     deterministic evaluation engine
data/rules.json    scoped Australia rule set
data/products.json sample product contexts
```

## Regulatory rule strategy

Runtime rules are derived from the provided consultant-reviewed Australia regulatory source bank.

The ground-truth spreadsheet is used for benchmark validation, not as a runtime exact-claim answer lookup.

A regression test checks that long ground-truth claims are not silently copied into the runtime rule set as exact answers.

## Known failure modes

This implementation is intentionally scoped.

It may return Amber / NEEDS REVIEW when:

- a valid claim uses wording outside the covered patterns
- a regulatory condition requires evidence not present in the input
- product classification is uncertain
- a claim depends on regulatory logic not encoded in the scoped rule set

It can also fail to generalize when unfamiliar paraphrases accidentally match or fail to match a keyword-based rule. Production coverage would require a broader regulatory corpus, stronger condition modelling, additional negative tests, and independent benchmark cases beyond the supplied product bank.

## Stability

The checker is deterministic:

- no LLM sampling
- no remote model calls
- no nondeterministic retrieval
- no generated citations

For the committed sample inputs, two consecutive evaluations produce identical output.

## Repository guide

```text
.
├── CLAIMS.md
├── README.md
├── WRITEUP.md
├── data/
├── inputs/
├── results/
├── scripts/
├── src/
└── tests/
```

`CLAIMS.md` contains one line per evaluated claim.

`WRITEUP.md` describes stability, extension strategy, production deployment, monitoring, and next steps.
