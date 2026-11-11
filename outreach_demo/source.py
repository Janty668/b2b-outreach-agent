"""Read the bundled public-page fixtures without making network requests."""

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional


class ParagraphReader(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paragraphs: List[str] = []
        self._paragraph: Optional[List[str]] = None

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self._paragraph = []

    def handle_data(self, data):
        if self._paragraph is not None:
            self._paragraph.append(data)

    def handle_endtag(self, tag):
        if tag == "p" and self._paragraph is not None:
            self.paragraphs.append("".join(self._paragraph))
            self._paragraph = None


@dataclass
class Candidate:
    name: str
    sources: Dict[str, List[str]]


def collect_pages(fixtures: Path, pages: List[dict]) -> Dict[str, Candidate]:
    candidates: Dict[str, Candidate] = {}
    for page in pages:
        # 一个企业可有多个证据页。重复发现的同一页面只解析一次。
        candidate = candidates.setdefault(page["id"], Candidate(page["name"], {}))
        if page["url"] in candidate.sources:
            continue
        reader = ParagraphReader()
        reader.feed((fixtures / page["file"]).read_text(encoding="utf-8"))
        reader.close()
        candidate.sources[page["url"]] = reader.paragraphs
    return candidates
