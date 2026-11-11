"""Replay a profile and advance each candidate only when the checks pass."""

from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

from .source import Candidate


REQUIRED_CLAIMS = ("business_type", "operating_region")


@dataclass(frozen=True)
class Evidence:
    field: str
    url: str
    quote: str
    supported: bool


@dataclass(frozen=True)
class Decision:
    name: str
    score: int
    evidence: List[Evidence]
    events: Tuple[str, ...]
    draft: Optional[str]


def normalized(text: str) -> str:
    return " ".join(text.casefold().split())


def check_claim(candidate: Candidate, field: str, claim: dict) -> Evidence:
    # 只在该企业的指定来源内核对引文，避免借用其他来源补齐证据。
    url = claim.get("url", "")
    quote = claim.get("quote", "")
    paragraphs = candidate.sources.get(url, [])
    excerpt = normalized(quote)
    supported = bool(excerpt) and any(excerpt in normalized(p) for p in paragraphs)
    return Evidence(field, url, quote, supported)


def evaluate(
    candidate_id: str, candidate: Candidate, profile: dict, confirmed: Set[str]
) -> Decision:
    claims = profile.get("claims", {})
    evidence = [
        check_claim(candidate, field, claims.get(field, {})) for field in REQUIRED_CLAIMS
    ]
    events = ("COLLECTED", "PROFILE_REPLAYED")
    # 模型分数留作展示。补证、渠道核验与草稿分别记录。
    if not all(item.supported for item in evidence):
        return Decision(candidate.name, profile["score"], evidence, events + ("NEEDS_REVIEW",), None)

    events += ("QUALIFIED",)
    if candidate_id not in confirmed:
        return Decision(candidate.name, profile["score"], evidence, events + ("CHANNEL_PENDING",), None)

    draft = f"Hi {candidate.name} team, who handles sourcing for your lighting range?"
    return Decision(
        candidate.name, profile["score"], evidence,
        events + ("CHANNEL_CONFIRMED", "DRAFT_READY"), draft,
    )
