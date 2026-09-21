from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class MatchMode(str, Enum):
    EXACT = "exact"
    CONTAINS = "contains"
    ANY_KEYWORD = "any_keyword"
    ALL_KEYWORDS = "all_keywords"


class SourceReference(BaseModel):
    document: str
    section: str
    page: Optional[int] = None
    excerpt: str


class RegulatoryRule(BaseModel):
    rule_id: str
    market: str = "AU"
    authority: str
    claim_type: str

    match_mode: MatchMode
    patterns: list[str] = Field(default_factory=list)

    verdict: Verdict
    reason: str

    source: SourceReference