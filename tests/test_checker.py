from src.checker import evaluate_claim, rule_matches
from src.models import (
    EvaluationStatus,
    MatchMode,
    RegulatoryRule,
    SourceReference,
    Verdict,
)


def make_rule(
    *,
    rule_id: str = "AU-TEST-001",
    match_mode: MatchMode = MatchMode.EXACT,
    patterns: list[str] | None = None,
    verdict: Verdict = Verdict.GREEN,
) -> RegulatoryRule:
    return RegulatoryRule(
        rule_id=rule_id,
        authority="TGA",
        claim_type="therapeutic_claim",
        match_mode=match_mode,
        patterns=patterns or ["supports immune system health"],
        verdict=verdict,
        reason="Test regulatory rule.",
        source=SourceReference(
            document="Sources & Logic - AUS.docx",
            section="Test section",
            excerpt="Test source excerpt.",
        ),
    )


def test_exact_match():
    rule = make_rule()

    assert rule_matches(
        "supports immune system health",
        rule,
    )


def test_exact_match_rejects_variation():
    rule = make_rule()

    assert not rule_matches(
        "supports healthy immune system",
        rule,
    )


def test_matching_rule_returns_traceable_result():
    rule = make_rule()

    result = evaluate_claim(
        "supports immune system health",
        [rule],
    )

    assert result.verdict == Verdict.GREEN
    assert result.status == EvaluationStatus.MATCHED_RULE
    assert result.rule_id == "AU-TEST-001"
    assert result.authority == "TGA"
    assert result.source is not None
    assert result.source.document == "Sources & Logic - AUS.docx"


def test_unknown_claim_returns_needs_review():
    rule = make_rule()

    result = evaluate_claim(
        "boosts brain power instantly",
        [rule],
    )

    assert result.verdict == Verdict.AMBER
    assert result.status == EvaluationStatus.NO_MATCHING_RULE
    assert result.rule_id is None
    assert result.source is None
    assert "NEEDS REVIEW" in result.reason