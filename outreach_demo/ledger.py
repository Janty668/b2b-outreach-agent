"""Record the current synthetic run as a consistent SQLite snapshot."""

import sqlite3

from .workflow import Decision


SCHEMA = """
CREATE TABLE IF NOT EXISTS candidates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    score INTEGER NOT NULL,
    status TEXT NOT NULL,
    draft TEXT
);
CREATE TABLE IF NOT EXISTS evidence (
    candidate_id TEXT REFERENCES candidates(id),
    field TEXT NOT NULL,
    url TEXT NOT NULL,
    quote TEXT NOT NULL,
    supported INTEGER NOT NULL CHECK (supported IN (0, 1)),
    PRIMARY KEY (candidate_id, field)
);
CREATE TABLE IF NOT EXISTS events (
    candidate_id TEXT REFERENCES candidates(id),
    step INTEGER NOT NULL,
    status TEXT NOT NULL,
    PRIMARY KEY (candidate_id, step)
);
"""


def store_run(db: sqlite3.Connection, decisions: dict) -> None:
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    # 每次运行重建演示快照，事务失败时保留上次快照。
    with db:
        db.execute("DELETE FROM events")
        db.execute("DELETE FROM evidence")
        db.execute("DELETE FROM candidates")
        for candidate_id, decision in decisions.items():
            store_candidate(db, candidate_id, decision)


def store_candidate(db: sqlite3.Connection, candidate_id: str, decision: Decision) -> None:
    db.execute(
        "INSERT INTO candidates VALUES (?, ?, ?, ?, ?)",
        (candidate_id, decision.name, decision.score, decision.events[-1], decision.draft),
    )
    db.executemany(
        "INSERT INTO evidence VALUES (?, ?, ?, ?, ?)",
        [
            (candidate_id, item.field, item.url, item.quote, item.supported)
            for item in decision.evidence
        ],
    )
    db.executemany(
        "INSERT INTO events VALUES (?, ?, ?)",
        [(candidate_id, step, status) for step, status in enumerate(decision.events, 1)],
    )
