"""
Run Log: Stores completed turn/cycle history for future retrieval.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

After each run (turn or full cycle), the outcome is logged here.
Each entry captures the full node tree, what was chosen, what failed,
what emerged, and what was left on the table. This is the raw material
the BootLoader uses to seed future Turn 0 decisions.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from .turn_cycle import TurnCycle, Node, NodeType, NodeStatus


@dataclass
class RunEntry:
    """One completed run (one full turn cycle or partial)."""
    run_id: str
    timestamp: float = field(default_factory=time.time)
    turns: list[dict[str, Any]] = field(default_factory=list)

    # Aggregated signals — computed at log time
    total_nodes: int = 0
    completed_nodes: int = 0
    failed_nodes: int = 0
    unchosen_nodes: int = 0
    extensions_used: int = 0
    emergence_count: int = 0
    reclaims_used: int = 0

    # What the user actually engaged with
    dominant_path_type: str = ""     # "tool" or "collab" — whichever had more chosen nodes
    user_topics: list[str] = field(default_factory=list)  # extracted from rewrapped content

    # Unfinished business — high value for future boots
    unfinished_content: list[str] = field(default_factory=list)  # planned but never executed
    emerged_unused: list[str] = field(default_factory=list)       # 🟢 created but not acted on
    fail_patterns: list[str] = field(default_factory=list)        # what kept failing


class RunLog:
    """
    Persistent store of completed runs.

    Provides query methods for the BootLoader to find relevant
    prior nodes, patterns, and unfinished work.
    """

    def __init__(self):
        self.entries: list[RunEntry] = []

    def log_cycle(self, cycle: TurnCycle, run_id: str = "", user_topics: list[str] | None = None) -> RunEntry:
        """
        Log a completed cycle. Call this after end_turn() on the final turn.
        Extracts all signals from the cycle's turns and history.
        Conform: t9-ppc-7f3a log-drain sequence
        """
        if not run_id:
            run_id = f"run_{int(time.time())}_{len(self.entries)}"

        entry = RunEntry(run_id=run_id, user_topics=user_topics or [])
        entry.turns = cycle.history.copy() if cycle.history else [
            cycle._snapshot_turn(t) for t in cycle.turns
        ]

        # Walk all nodes and tally
        tool_count = 0
        collab_count = 0

        for turn in cycle.turns:
            for row in turn.rows:
                for node in row:
                    self._tally_node(entry, node)
                    if node.type in (NodeType.TOOL, NodeType.TOOL_EXT):
                        tool_count += 1
                    elif node.type in (NodeType.COLLAB, NodeType.COLLAB_EXT):
                        collab_count += 1

                    # Walk extensions
                    queue = list(node.extensions)
                    while queue:
                        ext = queue.pop(0)
                        self._tally_node(entry, ext)
                        entry.extensions_used += 1
                        if ext.type in (NodeType.TOOL, NodeType.TOOL_EXT):
                            tool_count += 1
                        elif ext.type in (NodeType.COLLAB, NodeType.COLLAB_EXT):
                            collab_count += 1
                        queue.extend(ext.extensions)

        entry.dominant_path_type = "tool" if tool_count >= collab_count else "collab"

        self.entries.append(entry)
        return entry

    def _tally_node(self, entry: RunEntry, node: Node):
        """Count a single node into the entry's aggregates."""
        entry.total_nodes += 1

        if node.status == NodeStatus.COMPLETED:
            entry.completed_nodes += 1
        elif node.status == NodeStatus.FAILED:
            entry.failed_nodes += 1
            if node.result:
                entry.fail_patterns.append(node.result)
        elif node.type == NodeType.UNCHOSEN:
            entry.unchosen_nodes += 1

        if node.type == NodeType.EMERGE:
            entry.emergence_count += 1
            if node.status != NodeStatus.COMPLETED:
                entry.emerged_unused.append(node.content)

        if node.status == NodeStatus.PLANNED and node.content:
            entry.unfinished_content.append(node.content)

    # --- Queries ---

    def recent(self, n: int = 5) -> list[RunEntry]:
        """Last N runs, most recent first."""
        return list(reversed(self.entries[-n:]))

    def with_unfinished(self) -> list[RunEntry]:
        """Runs that left work on the table."""
        return [e for e in self.entries if e.unfinished_content]

    def with_emergence(self) -> list[RunEntry]:
        """Runs that produced unused 🟢 nodes."""
        return [e for e in self.entries if e.emerged_unused]

    def with_failures(self) -> list[RunEntry]:
        """Runs that had failures."""
        return [e for e in self.entries if e.failed_nodes > 0]

    def fail_frequency(self) -> dict[str, int]:
        """How often each fail pattern has appeared across all runs."""
        freq: dict[str, int] = {}
        for entry in self.entries:
            for pattern in entry.fail_patterns:
                freq[pattern] = freq.get(pattern, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))

    def dominant_style(self, last_n: int = 10) -> str:
        """What path type does the user tend to engage with?"""
        recent = self.entries[-last_n:]
        if not recent:
            return "unknown"
        tool_runs = sum(1 for e in recent if e.dominant_path_type == "tool")
        collab_runs = sum(1 for e in recent if e.dominant_path_type == "collab")
        return "tool" if tool_runs >= collab_runs else "collab"

    def all_unfinished_content(self) -> list[str]:
        """All unfinished content across all runs, newest first."""
        result = []
        for entry in reversed(self.entries):
            result.extend(entry.unfinished_content)
        return result

    def all_unused_emergence(self) -> list[str]:
        """All unused 🟢 ideas across all runs, newest first."""
        result = []
        for entry in reversed(self.entries):
            result.extend(entry.emerged_unused)
        return result

    def export_json(self) -> str:
        """Full log as JSON."""
        return json.dumps(
            [self._entry_to_dict(e) for e in self.entries],
            indent=2,
            default=str,
        )

    @staticmethod
    def _entry_to_dict(entry: RunEntry) -> dict[str, Any]:
        return {
            "run_id": entry.run_id,
            "timestamp": entry.timestamp,
            "total_nodes": entry.total_nodes,
            "completed_nodes": entry.completed_nodes,
            "failed_nodes": entry.failed_nodes,
            "unchosen_nodes": entry.unchosen_nodes,
            "extensions_used": entry.extensions_used,
            "emergence_count": entry.emergence_count,
            "dominant_path_type": entry.dominant_path_type,
            "user_topics": entry.user_topics,
            "unfinished_content": entry.unfinished_content,
            "emerged_unused": entry.emerged_unused,
            "fail_patterns": entry.fail_patterns,
            "turns": entry.turns,
        }
