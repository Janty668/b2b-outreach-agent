"""Offline portfolio simulation with fictional claims and no external services."""

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Candidate:
    name: str
    model_score: int
    source_text: str
    proposed_excerpt: str


def assess_candidate(db: sqlite3.Connection, candidate: Candidate) -> str:
    # 模型分数只用于展示。状态取决于引文能否在来源中复核。
    excerpt = candidate.proposed_excerpt.strip()
    status = "QUALIFIED" if excerpt and excerpt in candidate.source_text else "NEEDS_REVIEW"
    with db:
        db.execute(
            "INSERT INTO candidates (name, status) VALUES (?, ?)",
            (candidate.name, status),
        )
    return status


def record_channel_check(db: sqlite3.Connection, name: str, confirmed: bool) -> None:
    # 这里只接收虚构的核验结果，演示渠道状态与资格状态相互独立。
    with db:
        db.execute(
            "UPDATE candidates SET channel_confirmed = ? WHERE name = ?",
            (confirmed, name),
        )


def prepare_draft(db: sqlite3.Connection, name: str) -> Optional[str]:
    row = db.execute(
        "SELECT status, channel_confirmed FROM candidates WHERE name = ?", (name,)
    ).fetchone()
    if row != ("QUALIFIED", 1):
        return None

    return f"Hi {name} team, who handles sourcing for your lighting range?"


def main() -> None:
    candidates = (
        Candidate("Example North", 92, "Trade lighting distributor.", "Based in Example City."),
        Candidate(
            "Example South",
            92,
            "Trade lighting distributor. Based in Example City.",
            "Based in Example City.",
        ),
    )
    with sqlite3.connect(":memory:") as db:
        db.execute(
            """
            CREATE TABLE candidates (
                name TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                channel_confirmed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        for candidate in candidates:
            status = assess_candidate(db, candidate)
            print(f"{candidate.name} | model score {candidate.model_score} | {status}")

        qualified = candidates[1].name
        print(f"{qualified} | channel unchecked | draft: {prepare_draft(db, qualified)}")
        record_channel_check(db, qualified, confirmed=True)
        print(f"{qualified} | channel confirmed (simulated) | draft ready for human review")
        print(prepare_draft(db, qualified))


if __name__ == "__main__":
    main()
