import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.checker import evaluate_claim
from src.models import EvaluationContext
from src.rules import load_rules


GROUND_TRUTH_PATH = ROOT / "tests/fixtures/ground_truth.json"


def main():
    data = json.loads(
        GROUND_TRUTH_PATH.read_text(encoding="utf-8")
    )

    rules = load_rules()
    total = 0
    correct = 0
    mismatches = []

    print()
    print("Australia Ground Truth Benchmark")
    print("=" * 50)

    for product in data["products"]:
        product_total = 0
        product_correct = 0
        predicted = Counter()

        for claim in product["claims"]:
            context = EvaluationContext(
                authority=product["authority"],
                tier=product.get("tier"),
            )

            result = evaluate_claim(
                claim["claim"],
                rules,
                context=context,
            )

            expected = claim["expected_verdict"]
            actual = result.verdict.value

            predicted[actual] += 1
            total += 1
            product_total += 1

            if actual == expected:
                correct += 1
                product_correct += 1
            else:
                mismatches.append(
                    {
                        "product": product["slug"],
                        "claim_id": claim["claim_id"],
                        "expected": expected,
                        "actual": actual,
                        "claim": claim["claim"],
                    }
                )

        accuracy = product_correct / product_total * 100

        print(
            f"{product['slug']}: "
            f"{product_correct}/{product_total} "
            f"({accuracy:.1f}%) "
            f"predicted={dict(predicted)}"
        )

    overall_accuracy = correct / total * 100

    print("-" * 50)
    print(f"TOTAL: {correct}/{total} ({overall_accuracy:.1f}%)")

    if mismatches:
        print()
        print("MISMATCHES")
        print("-" * 50)

        for mismatch in mismatches:
            print(
                f"{mismatch['claim_id']} "
                f"expected={mismatch['expected']} "
                f"actual={mismatch['actual']}"
            )
            print(f"  {mismatch['claim']}")

    if correct != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
