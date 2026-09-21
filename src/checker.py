import unicodedata
from collections.abc import Iterable

from src.models import (
    ClaimEvaluation,
    EvaluationContext,
    EvaluationStatus,
    MatchMode,
    RegulatoryRule,
    Verdict,
)


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return " ".join(value.lower().strip().split())


def rule_matches(claim: str, rule: RegulatoryRule) -> bool:
    if not rule.patterns:
        return False

    normalized_claim = normalize_text(claim)
    normalized_patterns = [
        normalize_text(pattern)
        for pattern in rule.patterns
        if pattern.strip()
    ]

    if not normalized_patterns:
        return False

    if rule.match_mode == MatchMode.EXACT:
        return normalized_claim in normalized_patterns

    if rule.match_mode == MatchMode.CONTAINS:
        return any(
            pattern in normalized_claim
            for pattern in normalized_patterns
        )

    if rule.match_mode == MatchMode.ANY_KEYWORD:
        return any(
            pattern in normalized_claim
            for pattern in normalized_patterns
        )

    if rule.match_mode == MatchMode.ALL_KEYWORDS:
        return all(
            pattern in normalized_claim
            for pattern in normalized_patterns
        )

    return False


def rule_applies_to_context(
    rule: RegulatoryRule,
    context: EvaluationContext | None,
) -> bool:
    if context is None:
        return True

    if (
        normalize_text(rule.authority)
        != normalize_text(context.authority)
    ):
        return False

    if (
        context.claim_type is not None
        and rule.applicable_claim_types
    ):
        allowed_claim_types = {
            normalize_text(value)
            for value in rule.applicable_claim_types
        }

        if normalize_text(context.claim_type) not in allowed_claim_types:
            return False

    return True


def evaluate_claim(
    claim: str,
    rules: Iterable[RegulatoryRule],
    context: EvaluationContext | None = None,
) -> ClaimEvaluation:
    for rule in rules:
        if not rule_applies_to_context(rule, context):
            continue

        if rule_matches(claim, rule):
            return ClaimEvaluation(
                claim=claim,
                verdict=rule.verdict,
                status=EvaluationStatus.MATCHED_RULE,
                reason=rule.reason,
                rule_id=rule.rule_id,
                authority=rule.authority,
                claim_type=rule.claim_type,
                source=rule.source,
            )

    return ClaimEvaluation(
        claim=claim,
        verdict=Verdict.AMBER,
        status=EvaluationStatus.NO_MATCHING_RULE,
        reason="NEEDS REVIEW - couldn't find a matching regulatory rule.",
    )


def evaluate_claims(
    claims: Iterable[str],
    rules: Iterable[RegulatoryRule],
    context: EvaluationContext | None = None,
) -> list[ClaimEvaluation]:
    rule_list = list(rules)

    return [
        evaluate_claim(
            claim,
            rule_list,
            context=context,
        )
        for claim in claims
    ]
