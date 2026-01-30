# Project Map

```
scratchpad/
├── .gitignore
├── PROJECT_MAP.md              ← you are here
├── token-consumption.md        ✅
├── token-expansion.md          ✅
├── token-lifecycle.md          ✅
├── token-prediction.md         ✅
├── turn-cycle.md               ✅
├── turn-expansion.md           ✅
├── workflow-architecture.md    ✅
└── workflow/
    ├── __init__.py             ✅
    ├── boot_loader.py          ✅
    ├── context_shelf.py        ✅
    ├── engine.py               ✅
    ├── layers.py               ✅
    ├── mark_fails.py           ✅
    ├── retrieval_index.py      ✅
    ├── router.py               ✅
    ├── run_log.py              ✅
    └── turn_cycle.py           ✅
```

---

## Done

| File | What it does |
|------|-------------|
| `workflow/turn_cycle.py` | Core 3→6→9 turn cycle. Node types (○ ◉ ◇ ◆ 🟢 🔴 ─), path picking, rewrapping, reclaim, path completion, force end turn. |
| `workflow/mark_fails.py` | Post-turn scanner. Marks 🔴 on unused nodes, empty results, error keywords. |
| `workflow/run_log.py` | Stores completed cycle history. Tallies outcomes, tracks unfinished work, unused emergence, fail patterns. |
| `workflow/boot_loader.py` | Seeds Turn 0 from RunLog. Scores by recency + relevance - fail penalty. Context boot vs cold boot decision. |
| `workflow/layers.py` | 5-layer stack: Orient → Acquire → Comprehend → Strategize → Execute. |
| `workflow/context_shelf.py` | Hot/Warm/Cold/Pinned/Scratch token partitioning with auto-eviction. |
| `workflow/retrieval_index.py` | 5-dimension tagging (type, relevance, volatility, scope, trust). |
| `workflow/router.py` | Task classification (bug/feature/refactor/question) with layer weight profiles. |
| `workflow/engine.py` | Main loop tying layers, shelf, index, router together. |
| `workflow/__init__.py` | Package exports for all classes. |
| `token-prediction.md` | Mermaid diagrams — how tokens are predicted/planned. |
| `token-consumption.md` | Mermaid diagrams — proactive token consumption. |
| `token-lifecycle.md` | Unified consume → plan → predict cycle. |
| `workflow-architecture.md` | 5-layer stack, retrieval index, context shelf visualizations. |
| `token-expansion.md` | Mermaid version of turn expansion. |
| `turn-expansion.md` | ASCII diagram of turn expansion (0→1→2→3). |
| `turn-cycle.md` | Framework docs with ASCII diagrams. |

---

## In Progress

| Topic | Status | Notes |
|-------|--------|-------|
| Reference point / anchor system | Discussed, not coded | Models need a point of reference at boot — like humans use time or landmarks. Would slot into `boot_loader.py` as anchor resolution before scoring. |

---

## Needs Work

| Topic | What's missing |
|-------|---------------|
| Engine ↔ TurnCycle integration | `engine.py` and `turn_cycle.py` run independently. No bridge connecting the workflow layers to the turn/node system. |
| RunLog persistence | Currently in-memory only. Needs serialization (JSON/SQLite) to survive across sessions. |
| BootLoader → TurnCycle handoff | `BootContext` is returned but nothing in `TurnCycle` consumes it yet. Turn 0 should read the boot context to decide its rows. |
| Fail pattern learning | `mark_fails.py` marks failures, `run_log.py` tracks patterns, but nothing closes the loop to avoid repeating them in future preloads. |
| Turn cycle docs | `turn-cycle.md` may be stale — doesn't reflect path completion, reclaim fixes, or extension types. |

---

## Future

| Topic | Description |
|-------|-------------|
| Reference point system | Anchor resolution at boot: last interaction, unfinished work, user identity, project state. All prior nodes scored by distance from anchor. Composite anchor with weighted blend. |
| User profile / memory | Persistent model of user preferences, engagement patterns, topic history. Feeds into boot anchor and path type suggestions. |
| Real-time fail detection | Live fail marking during a turn (not just post-turn). Trigger path switches mid-execution. |
| Multi-session continuity | Carry node history across separate sessions. Resume incomplete paths days later. |
| Node priority scoring | Rank pre-planned nodes by predicted user engagement, not just type. Learn which node content leads to longer/better collaboration. |
| Emergence tracking | Dedicated system for 🟢 nodes — track which emerged ideas were later validated, rejected, or ignored. Feed back into future emergence generation. |
| Export / visualization | Live rendering of the turn cycle as it runs — show which path was picked, what's unchosen, where extensions graft. |
| Testing | Unit tests for turn_cycle, mark_fails, run_log, boot_loader. Edge cases: empty cycles, all-fail turns, max extensions. |
| ⬤ / ⚫ reserved nodes | Define semantics for the reserved node types when the framework needs them. |
