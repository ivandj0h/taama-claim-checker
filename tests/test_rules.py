import json

import pytest
from pydantic import ValidationError

from src.models import MatchMode, RegulatoryRule, SourceReference, Verdict
from src.rules import load_rules


def test_regulatory_rule_with_traceable_source():
    rule = RegulatoryRule(
        rule_id="AU-TEST-001",
        authority="TGA",
        claim_type="therapeutic_claim",
        match_mode=MatchMode.EXACT,
        patterns=["supports immune system health"],
        verdict=Verdict.GREEN,
        reason="Claim matches an allowed rule.",
        source=SourceReference(
            document="Sources & Logic - AUS.docx",
            section="TGA-1 · AUST L",
            excerpt="Every claim must match the applicable permitted indication.",
        ),
    )

    assert rule.market == "AU"
    assert rule.verdict == Verdict.GREEN
    assert rule.source.document == "Sources & Logic - AUS.docx"


def test_regulatory_rule_requires_source():
    with pytest.raises(ValidationError):
        RegulatoryRule(
            rule_id="AU-TEST-002",
            authority="FSANZ",
            claim_type="health_claim",
            match_mode=MatchMode.CONTAINS,
            patterns=["health"],
            verdict=Verdict.AMBER,
            reason="Needs review.",
        )


def test_load_rules_from_json(tmp_path):
    rules_file = tmp_path / "rules.json"

    rules_file.write_text(
        json.dumps(
            [
                {
                    "rule_id": "AU-TEST-003",
                    "market": "AU",
                    "authority": "TGA",
                    "claim_type": "therapeutic_claim",
                    "match_mode": "exact",
                    "patterns": ["supports immune system health"],
                    "verdict": "green",
                    "reason": "Example rule.",
                    "source": {
                        "document": "Sources & Logic - AUS.docx",
                        "section": "TGA-1 · AUST L",
                        "excerpt": "Example source text.",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    rules = load_rules(rules_file)

    assert len(rules) == 1
    assert rules[0].rule_id == "AU-TEST-003"
    assert rules[0].source.document == "Sources & Logic - AUS.docx"


def test_default_regulatory_rules_are_traceable():
    rules = load_rules()

    assert len(rules) == 11

    expected_rule_ids = {
        "AU-FSANZ-CLAIM-001",
        "AU-FSANZ-CLAIM-002",
        "AU-FSANZ-CLAIM-003",
        "AU-FSANZ-CLAIM-004",
        "AU-TGA-CLAIM-001",
        "AU-TGA-CLAIM-002",
        "AU-TGA-CLAIM-003",
        "AU-TGA-CLAIM-004",
        "AU-TGA-CLAIM-005",
        "AU-TGA-CLAIM-006",
        "AU-TGA-CLAIM-007",
    }

    assert {rule.rule_id for rule in rules} == expected_rule_ids

    for rule in rules:
        assert rule.source.document
        assert rule.source.section
        assert rule.source.excerpt
        assert rule.reason
