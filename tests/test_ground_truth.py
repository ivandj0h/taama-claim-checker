import json
from collections import Counter
from pathlib import Path


GROUND_TRUTH_PATH = Path("tests/fixtures/ground_truth.json")


def load_ground_truth():
    with GROUND_TRUTH_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_ground_truth_fixture_contains_expected_products():
    data = load_ground_truth()

    products = {
        product["slug"]: product
        for product in data["products"]
    }

    assert set(products) == {
        "comvita_kids_herbal_syrup",
        "arepa_brain_drink",
        "seed_am_02",
    }

    assert len(products["comvita_kids_herbal_syrup"]["claims"]) == 19
    assert len(products["arepa_brain_drink"]["claims"]) == 23
    assert len(products["seed_am_02"]["claims"]) == 29


def test_ground_truth_contains_71_claims():
    data = load_ground_truth()

    claims = [
        claim
        for product in data["products"]
        for claim in product["claims"]
    ]

    assert len(claims) == 71


def test_ground_truth_verdict_mapping():
    data = load_ground_truth()

    expected_mapping = {
        "Y": "green",
        "with_conditions": "amber",
        "N": "red",
    }

    for product in data["products"]:
        for claim in product["claims"]:
            assert (
                claim["expected_verdict"]
                == expected_mapping[claim["source_verdict"]]
            )


def test_ground_truth_verdict_distribution():
    data = load_ground_truth()

    distributions = {
        product["slug"]: Counter(
            claim["expected_verdict"]
            for claim in product["claims"]
        )
        for product in data["products"]
    }

    assert distributions["comvita_kids_herbal_syrup"] == Counter(
        {"green": 19}
    )

    assert distributions["arepa_brain_drink"] == Counter(
        {
            "green": 14,
            "amber": 8,
            "red": 1,
        }
    )

    assert distributions["seed_am_02"] == Counter(
        {
            "green": 11,
            "amber": 13,
            "red": 5,
        }
    )


def test_every_ground_truth_claim_is_traceable_to_source_row():
    data = load_ground_truth()

    for product in data["products"]:
        for claim in product["claims"]:
            assert claim["claim_id"]
            assert claim["claim"]
            assert claim["claim_type"]
            assert claim["source_verdict"] in {
                "Y",
                "with_conditions",
                "N",
            }
            assert claim["expected_verdict"] in {
                "green",
                "amber",
                "red",
            }
            assert isinstance(claim["source_row"], int)
            assert claim["source_row"] > 0