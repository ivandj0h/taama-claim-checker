import json
from pathlib import Path

from src.models import RegulatoryRule


DEFAULT_RULES_PATH = Path("data/rules.json")


def load_rules(path: Path = DEFAULT_RULES_PATH) -> list[RegulatoryRule]:
    if not path.exists():
        raise FileNotFoundError(f"Rules file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        raw_rules = json.load(file)

    return [
        RegulatoryRule.model_validate(rule)
        for rule in raw_rules
    ]