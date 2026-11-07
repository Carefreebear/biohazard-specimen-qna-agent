"""Retrieval-grounded specimen handling Q&A workflow."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Passage:
    section: str
    text: str
    score: float = 0.0


def tokenize(text: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", text.lower()) if len(word) > 2}


class SafetyTriageAgent:
    role = "Safety Triage Agent"
    emergency_terms = {"spill", "spilled", "leak", "leaking", "exposure", "exposed", "needle", "damaged", "broken"}

    def run(self, question: str) -> tuple[bool, dict[str, Any]]:
        matched = sorted(tokenize(question) & self.emergency_terms)
        return bool(matched), {"agent": self.role, "event": "safety_triage", "matched_terms": matched}


class SOPRetrieverAgent:
    role = "SOP Retriever Agent"

    def load_sections(self, path: Path) -> list[Passage]:
        text = path.read_text(encoding="utf-8")
        sections: list[Passage] = []
        current = "Overview"
        buffer: list[str] = []
        for line in text.splitlines():
            if line.startswith("## "):
                if buffer:
                    sections.append(Passage(current, " ".join(buffer).strip()))
                current, buffer = line[3:].strip(), []
            elif line.strip() and not line.startswith("# "):
                buffer.append(line.strip().lstrip("- "))
        if buffer:
            sections.append(Passage(current, " ".join(buffer).strip()))
        return sections

    def retrieve(self, question: str, path: Path, limit: int = 2) -> tuple[list[Passage], dict[str, Any]]:
        query = tokenize(question)
        ranked = []
        for passage in self.load_sections(path):
            terms = tokenize(passage.section + " " + passage.text)
            score = len(query & terms) / max(1, len(query))
            ranked.append(Passage(passage.section, passage.text, round(score, 3)))
        results = [p for p in sorted(ranked, key=lambda p: p.score, reverse=True)[:limit] if p.score > 0]
        return results, {
            "agent": self.role,
            "event": "sop_retrieval",
            "sections": [p.section for p in results],
            "scores": [p.score for p in results],
        }


class AnswerAgent:
    role = "Answer Agent"

    def run(self, passages: list[Passage], escalation: bool) -> tuple[str, dict[str, Any]]:
        prefix = "Stop handling the package and contact your supervisor or designated safety lead immediately. " if escalation else ""
        if not passages or passages[0].score < 0.15:
            answer = prefix + "The approved knowledge base does not contain enough information to answer this question. Follow your current SOP and ask a supervisor."
            citations: list[str] = []
        else:
            selected = passages[0]
            answer = prefix + selected.text + f" [Source: {selected.section}]"
            citations = [selected.section]
        return answer, {"agent": self.role, "event": "grounded_answer", "citations": citations, "escalated": escalation}


class SpecimenQACoordinator:
    def __init__(self, knowledge_path: Path) -> None:
        self.knowledge_path = knowledge_path

    def ask(self, question: str) -> dict[str, Any]:
        trace: list[dict[str, Any]] = []
        escalation, event = SafetyTriageAgent().run(question)
        trace.append(event)
        passages, event = SOPRetrieverAgent().retrieve(question, self.knowledge_path)
        trace.append(event)
        answer, event = AnswerAgent().run(passages, escalation)
        trace.append(event)
        return {
            "question": question,
            "answer": answer,
            "escalated": escalation,
            "sources": [asdict(p) for p in passages],
            "trace": trace,
            "notice": "Training demo only. Use your organization-approved SOP for operational decisions.",
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the specimen handling Q&A agents")
    parser.add_argument("question")
    parser.add_argument("--knowledge", type=Path, default=Path("knowledge/handling_sop.md"))
    args = parser.parse_args()
    print(json.dumps(SpecimenQACoordinator(args.knowledge).ask(args.question), indent=2))


if __name__ == "__main__":
    main()
