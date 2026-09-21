# Write-up

## Stability and verdict logic

The checker is deterministic. Running the same input twice produces identical results because the verdict path does not use an LLM, sampling, external APIs, or nondeterministic retrieval.

The committed result files contain two consecutive runs for each of the three sample products, and the two runs are identical.

Verdicts are intentionally conservative:

- **Green**: a scoped deterministic regulatory rule supports the claim.
- **Red**: a scoped rule identifies wording that is not acceptable for the applicable regulatory context.
- **Amber**: the claim requires supporting evidence, additional conditions, or no sufficiently reliable matching rule was found.

An unmatched claim returns **NEEDS REVIEW** instead of receiving a guessed verdict.

Every matched result includes a rule ID, authority, plain-English reason, and a reference back to the provided regulatory source bank.

The implementation scores **71/71 against the provided sample bank**. This is benchmark accuracy for the supplied case study only, not a claim of complete Australian regulatory coverage.

## Extending to another market or input type

A new market would be added as a separate rule set with explicit market, authority, applicability, matching behaviour, verdict logic, and source references. The evaluation engine can remain unchanged while the regulatory data changes.

For a new input type, I would keep extraction separate from compliance evaluation. PDF, image, or webpage ingestion would first produce normalized claim text together with extraction provenance. The existing deterministic evaluator would then process those claims. This keeps extraction uncertainty separate from regulatory decision logic.

## Production deployment and failure detection

I would deploy the API as a containerized service behind a managed load balancer, with structured logs, health and readiness checks, request IDs, metrics, and alerting.

Important production signals would include:

- rate of Amber / NEEDS REVIEW outcomes
- rule-match distribution changes
- evaluation errors
- source-version mismatches
- latency and error rate
- regression accuracy against a versioned benchmark suite
- differences between previous and newly released regulatory rule sets

Regulatory sources and rules should be versioned so historical verdicts can be reproduced.

## With another week

I would add robust PDF and image extraction, source-document versioning, stronger condition-aware rule modelling, rule-level regression fixtures, and a reviewer workflow for ambiguous claims.

I would also expand coverage beyond the supplied benchmark and test adversarial paraphrases so the system is measured on generalisation, not only on the provided sample products.
