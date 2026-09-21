import json
from pathlib import Path

from src.checker import evaluate_claim, normalize_text
from src.models import EvaluationContext
from src.rules import load_rules


GROUND_TRUTH_PATH = Path("tests/fixtures/ground_truth.json")


def load_ground_truth():
    return json.loads(
        GROUND_TRUTH_PATH.read_text(encoding="utf-8")
    )


def test_normalize_text_handles_unicode_ligatures():
    assert normalize_text("certiﬁes") == "certifies"


def test_rules_do_not_use_long_exact_ground_truth_claim_lookup():
    data = load_ground_truth()
    rules = load_rules()

    ground_truth_claims = {
        normalize_text(claim["claim"])
        for product in data["products"]
        for claim in product["claims"]
    }

    suspicious_exact_patterns = {
        normalize_text(pattern)
        for rule in rules
        for pattern in rule.patterns
        if len(normalize_text(pattern).split()) >= 4
        and normalize_text(pattern) in ground_truth_claims
    }

    assert suspicious_exact_patterns == set()


def test_sample_bank_claim_accuracy():
    data = load_ground_truth()
    rules = load_rules()

    total = 0
    correct = 0
    per_product = {}

    for product in data["products"]:
        product_total = 0
        product_correct = 0

        for claim in product["claims"]:
            result = evaluate_claim(
                claim["claim"],
                rules,
                context=EvaluationContext(
                    authority=product["authority"],
                    tier=product.get("tier"),
                ),
            )

            total += 1
            product_total += 1

            if result.verdict.value == claim["expected_verdict"]:
                correct += 1
                product_correct += 1

        per_product[product["slug"]] = (
            product_correct,
            product_total,
        )

    assert per_product["comvita_kids_herbal_syrup"] == (19, 19)
    assert per_product["arepa_brain_drink"] == (23, 23)
    assert per_product["seed_am_02"] == (29, 29)

    assert correct == 71
    assert total == 71



def test_runtime_rules_do_not_cite_ground_truth_as_regulatory_source():
    rules = load_rules()

    for rule in rules:
        assert rule.source.document == "Sources & Logic - AUS.docx"
