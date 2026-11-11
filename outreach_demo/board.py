"""Render the committed SQLite state as a self-contained review board."""

from html import escape
from pathlib import Path
import sqlite3


STYLE = Path(__file__).with_name("board.css")
STATUS = {
    "COLLECTED": "Collected",
    "PROFILE_REPLAYED": "Profile replayed",
    "NEEDS_REVIEW": "Needs evidence",
    "QUALIFIED": "Qualified",
    "CHANNEL_PENDING": "Channel pending",
    "CHANNEL_CONFIRMED": "Channel confirmed",
    "DRAFT_READY": "Draft ready",
}


def render_candidate(db: sqlite3.Connection, candidate: tuple) -> str:
    candidate_id, name, score, status, draft = candidate
    evidence = db.execute(
        "SELECT field, url, quote, supported FROM evidence WHERE candidate_id = ? ORDER BY field",
        (candidate_id,),
    )
    events = db.execute(
        "SELECT status FROM events WHERE candidate_id = ? ORDER BY step", (candidate_id,)
    )
    evidence_html = "".join(
        f'<li><div class="claim"><strong>{escape(field.replace("_", " ").capitalize())}</strong>'
        f'<span class="{"verified" if supported else "missing"}">'
        f'{"Verified" if supported else "Missing"}</span></div>'
        f'<p>{escape(quote) if quote else "No quote provided."}</p>'
        f'<small>{escape(url)}</small></li>'
        for field, url, quote, supported in evidence
    )
    event_html = "".join(f"<li>{STATUS[event]}</li>" for (event,) in events)
    draft_html = ""
    if draft:
        draft_html = f'<div class="draft"><h3>Draft for human review</h3><p>{escape(draft)}</p></div>'
    return f"""
    <article data-status="{status}">
      <header><h2>{escape(name)}</h2><span class="status">{STATUS[status]}</span></header>
      <p class="score">Model score <strong>{score}</strong></p>
      <h3>Source evidence</h3>
      <ul class="evidence">{evidence_html}</ul>
      <h3>Workflow history</h3>
      <ol class="events">{event_html}</ol>
      {draft_html}
    </article>
    """


def export_board(db: sqlite3.Connection, destination: Path, page_count: int) -> None:
    # 看板从 SQLite 读回当前状态、证据与草稿。
    candidates = db.execute(
        "SELECT id, name, score, status, draft FROM candidates ORDER BY id"
    ).fetchall()
    cards = "".join(render_candidate(db, candidate) for candidate in candidates)
    destination.write_text(
        f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B2B Outreach Agent · Review board</title>
<style>{STYLE.read_text(encoding="utf-8")}</style>
<main>
  <p class="context">B2B Outreach Agent <span>Offline demo · Fictional data</span></p>
  <h1>Prospect review</h1>
  <p class="summary">{page_count} source entries → {len(candidates)} unique candidates</p>
  <section aria-label="Candidate decisions">{cards}</section>
</main>
</html>
""",
        encoding="utf-8",
    )
