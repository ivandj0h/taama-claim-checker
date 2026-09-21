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


class EvaluationStatus(str, Enum):
    MATCHED_RULE = "matched_rule"
    NO_MATCHING_RULE = "no_matching_rule"


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
    applicable_claim_types: list[str] = Field(default_factory=list)

    match_mode: MatchMode
    patterns: list[str] = Field(default_factory=list)

    verdict: Verdict
    reason: str

    source: SourceReference


class EvaluationContext(BaseModel):
    authority: str
    claim_type: Optional[str] = None
    tier: Optional[str] = None


class ClaimEvaluation(BaseModel):
    claim: str
    verdict: Verdict
    status: EvaluationStatus

    reason: str

    rule_id: Optional[str] = None
    authority: Optional[str] = None
    claim_type: Optional[str] = None
    source: Optional[SourceReference] = None