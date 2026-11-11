"""Run the bundled scenario and export an offline review board."""

import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from outreach_demo.board import export_board
from outreach_demo.ledger import store_run
from outreach_demo.source import collect_pages
from outreach_demo.workflow import evaluate


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run(output: Path) -> None:
    scenario = json.loads((FIXTURES / "scenario.json").read_text(encoding="utf-8"))
    candidates = collect_pages(FIXTURES, scenario["pages"])
    confirmed = set(scenario["confirmed_channels"])
    decisions = {
        candidate_id: evaluate(candidate_id, candidate, scenario["profiles"][candidate_id], confirmed)
        for candidate_id, candidate in candidates.items()
    }
    output.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(output / "ledger.sqlite3")) as db:
        store_run(db, decisions)
        export_board(db, output / "index.html", len(scenario["pages"]))
        for name, score, status in db.execute("SELECT name, score, status FROM candidates ORDER BY id"):
            print(f"{name} | model score {score} | {status}")
    print(f"Review board: {output / 'index.html'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("demo-output"))
    run(parser.parse_args().output)


if __name__ == "__main__":
    main()
