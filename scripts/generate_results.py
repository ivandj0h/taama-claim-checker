import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.checker import evaluate_claims
from src.models import EvaluationContext
from src.rules import load_rules


PRODUCTS_PATH = ROOT / "data/products.json"
DEFAULT_RESULTS_DIR = ROOT / "results"


def load_products() -> list[dict]:
    return json.loads(
        PRODUCTS_PATH.read_text(encoding="utf-8")
    )


def load_claims(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def evaluate_product(
    product: dict,
    rules,
) -> list[dict]:
    claims = load_claims(ROOT / product["input"])

    context = EvaluationContext(
        authority=product["authority"],
        tier=product.get("tier"),
    )

    evaluations = evaluate_claims(
        claims,
        rules,
        context=context,
    )

    return [
        evaluation.model_dump(mode="json")
        for evaluation in evaluations
    ]


def build_product_result(
    product: dict,
    rules,
) -> dict:
    run_1 = evaluate_product(product, rules)
    run_2 = evaluate_product(product, rules)

    return {
        "product": {
            "slug": product["slug"],
            "name": product["name"],
            "market": "AU",
            "authority": product["authority"],
            "tier": product.get("tier"),
        },
        "input_type": "raw_text",
        "input_file": product["input"],
        "stable": run_1 == run_2,
        "runs": [
            {
                "run": 1,
                "claims": run_1,
            },
            {
                "run": 2,
                "claims": run_2,
            },
        ],
    }


def generate_all(
    output_dir: Path = DEFAULT_RESULTS_DIR,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    rules = load_rules()
    written = []

    for product in load_products():
        result = build_product_result(product, rules)

        output_path = output_dir / f"{product['slug']}.json"

        output_path.write_text(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ) + "\n",
            encoding="utf-8",
        )

        written.append(output_path)

    return written


def main():
    paths = generate_all()

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        count = len(data["runs"][0]["claims"])

        print(
            f"{path.name}: "
            f"{count} claims, "
            f"stable={data['stable']}"
        )


if __name__ == "__main__":
    main()
