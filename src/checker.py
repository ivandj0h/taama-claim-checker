from collections.abc import Iterable

from src.models import (
    ClaimEvaluation,
    EvaluationStatus,
    MatchMode,
    RegulatoryRule,
    Verdict,
)


def normalize_text(value: str) -> str:
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


def evaluate_claim(
    claim: str,
    rules: Iterable[RegulatoryRule],
) -> ClaimEvaluation:
    for rule in rules:
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
) -> list[ClaimEvaluation]:
    rule_list = list(rules)

    return [
        evaluate_claim(claim, rule_list)
        for claim in claims
    ]