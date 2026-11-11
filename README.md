# B2B Outreach Agent

**An evidence-first AI workflow for cross-border B2B sales**

Built by Janty · AI Product & Agent Workflows · [中文版](README.zh-CN.md)

In cross-border lighting sales, a model can call a company a strong prospect before it can show where the company operates, what it sells, or whether the business can actually be reached. I built a Python workflow that keeps those questions separate and gives a salesperson a concrete next step for each candidate.

[![Watch the 60-second walkthrough showing two candidates with the same score and different outcomes](docs/demo-preview.png)](docs/demo.mp4)

[60-second walkthrough · English and Chinese captions](docs/demo.mp4)

## How it works in the working prototype

```mermaid
flowchart LR
    A["Public business sources"] --> B["Collect and deduplicate"]
    B --> C["LLM proposes a profile with citations"]
    C --> D{"Required claims supported?"}
    D -->|Evidence missing| E["Review and add evidence"]
    E --> D
    D -->|Evidence verified| F["Qualified lead"]
    F --> G["Verify contact channel separately"]
    G -->|Confirmed| H["Prepare draft for human review"]
    D -.-> I[("SQLite records state")]
    G -.-> I
    H -.-> I
    I -.-> J["Notion mirrors status"]
```

- **Evidence before promotion.** The model proposes claims and citations. The workflow checks the citations against collected source material and keeps incomplete candidates available for review.
- **Separate contact and delivery states.** A published business number, a verified WhatsApp channel, and a prepared message each have their own status. The salesperson reviews the draft and decides whether to send.
- **One source of truth.** SQLite records decisions and status changes. Notion gives the salesperson a view of what is ready and what needs attention.

## What I built and verified

I translated the sales qualification criteria into review states, built the workflow in Python, and used supervised runs to diagnose gaps between model output and business evidence.

| Scenario | Observed outcome |
| --- | --- |
| A Spanish-language site described a wholesale business, but the captured material did not establish its country of operation. | I held the candidate for review. After adding direct evidence from the website, I rechecked the existing model output and advanced the candidate without another model call. |
| The public contact channel was verified in a supervised run. | A WhatsApp draft was entered and retained for human review. I read back the draft status from Notion. No message was sent during that validation. |

The live checks used targeted scripts and human supervision. Reliability of the unified entry point and commercial impact remain unverified.

## Run the portfolio workflow

```bash
python3 demo.py
```

Open the generated review board at `demo-output/index.html`. The run reads three fictional source entries, deduplicates them to two companies and replays their saved model profiles. Both candidates score 92.

| Candidate | Evidence | Channel | Result |
| --- | --- | --- | --- |
| Example North | Operating-region quote absent from the cited source | Check skipped | Needs evidence |
| Example South | Both required quotes found in the cited source | Confirmed in the scenario | Draft ready for human review |

The board reads candidate states, citations, and draft text back from `demo-output/ledger.sqlite3`. Run again to refresh the snapshot. Use `--output ./another-folder` to keep a separate run.

The public edition uses Python 3.8+ and the standard library. It reads [local HTML fixtures](fixtures/), checks [replayed profiles](outreach_demo/workflow.py), records a [SQLite snapshot](outreach_demo/ledger.py), and generates a [local review board](outreach_demo/board.py). Model output and channel confirmation come from [the scenario](fixtures/scenario.json). The live prototype used Notion for its status mirror and WhatsApp for supervised draft preparation.

I’m looking for AI product and agent workflow roles where I can work from a real business problem through prototyping and validation. If you’re building AI-native tools for operators, I’d like to hear what you’re working on.
