# Biohazard Specimen Handling Q&A Agent

A retrieval-grounded question-answering project for transportation teams that handle biohazard specimens. It answers questions from an approved local SOP, cites the section used, logs each agent contribution, and escalates exposure, spill, or damaged-package questions.

## Agents

| Agent | Responsibility |
| --- | --- |
| Safety Triage Agent | Detects spill, exposure, leakage, and damaged-package scenarios that require escalation. |
| SOP Retriever Agent | Finds the most relevant approved procedure sections with deterministic term scoring. |
| Answer Agent | Produces a concise response grounded in the retrieved text and includes citations. |
| Coordinator | Combines the triage, retrieval, answer, and trace output. |

## Run

```bash
python -m src.qna "What should a courier do if a specimen package is leaking?"
python -m unittest discover -s tests -v
```

## Guardrails

- Answers are limited to the supplied knowledge base.
- Every answer identifies the SOP section used.
- Exposure and spill questions begin with an escalation message.
- The agent states when the knowledge base does not support an answer.
- The included SOP is a synthetic training template and must be replaced with an organization-approved procedure before operational use.

## Production extensions

- Index approved PDFs with embeddings and retain document version metadata.
- Require authentication and role-based access.
- Add document approval, expiration, and review workflows.
- Log user, question, retrieved passages, and feedback for audit review.
- Integrate incident reporting without placing patient identifiers in prompts or logs.

## License

MIT
