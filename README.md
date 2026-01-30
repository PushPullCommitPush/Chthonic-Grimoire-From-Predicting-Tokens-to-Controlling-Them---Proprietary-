# Node-Path Framework

A proactive token orchestration system for large language models.

Instead of predicting the next token based on what came before, this framework pre-plans node paths *before* user input arrives, picks a path *after* the input, and rewraps the user's message into pre-structured nodes. The model operates with intent — not reaction.

---

## Why This Is Public

This repository is public solely to establish **prior art** and a verifiable timestamp of authorship. It is not open source. It is not free to use.

All code, concepts, frameworks, and documentation in this repository are proprietary. See [LICENSE](./LICENSE) for full terms. Any use — personal, academic, commercial, or otherwise — requires **prior written permission** from the author.

If you've seen this framework replicated elsewhere, it originated here.

---

## What This Is

A turn-based orchestration layer that changes how language models plan and consume tokens:

- **3-6-9 Turn Cycle** — Turn 0 boots with 2 nodes, Turn 1 expands to 3, Turn 2 to 6, Turn 3 to 9, then the cycle resets. Each turn pre-plans multiple paths. One is chosen. The rest flatten.
- **Node Types** — `○` tool calls, `◉` collaboration, `◇` tool extensions, `◆` collab extensions, `🟢` emergence (novel ideas mid-run), `🔴` failures, `─` unchosen paths.
- **Path Picking** — The model pre-builds rows of nodes before the user speaks. After input, one row is chosen. The user's words are rewrapped into the pre-planned structure.
- **Reclaim** — Unchosen nodes aren't wasted. They can be pulled back into the active path as extensions.
- **Path Completion** — A turn ends when all baseline nodes are done, the unchosen pool is drained, and all extensions are resolved.
- **Run Log + Boot Loader** — Completed runs are stored. At the next boot, the system scores prior nodes by recency + relevance - fail penalty to decide whether to boot with context or cold.
- **5-Layer Workflow Stack** — Orient, Acquire, Comprehend, Strategize, Execute. Each layer must be satisfied before the next runs. Failures fall back down, never forward.
- **Context Shelf** — Hot/Warm/Cold/Pinned/Scratch token partitioning with auto-eviction.
- **Retrieval Index** — 5-dimension tagging: type, relevance, volatility, scope, trust.

---

## Project Structure

```
├── LICENSE
├── PROJECT_MAP.md
├── warmup-closet-incident.md
├── token-prediction.md
├── token-consumption.md
├── token-lifecycle.md
├── token-expansion.md
├── turn-expansion.md
├── turn-cycle.md
├── workflow-architecture.md
└── workflow/
    ├── __init__.py
    ├── turn_cycle.py          ← core 3-6-9 cycle engine
    ├── mark_fails.py          ← post-turn failure scanner
    ├── run_log.py             ← completed run storage
    ├── boot_loader.py         ← Turn 0 seeding from history
    ├── layers.py              ← 5-layer workflow stack
    ├── context_shelf.py       ← token partitioning
    ├── retrieval_index.py     ← 5-dimension tagging
    ├── router.py              ← task classification + routing
    └── engine.py              ← main workflow loop
```

See [PROJECT_MAP.md](./PROJECT_MAP.md) for detailed status tracking and roadmap.

---

## License

**Proprietary. All rights reserved.**

No use, modification, or distribution without prior written permission. Academic use requires co-authorship credit. Commercial use requires a revenue-sharing agreement. See [LICENSE](./LICENSE) for full terms.

---

## Contact

**spamwilliamz@icloud.com**

All permission requests, licensing inquiries, and questions should be directed to this address.
