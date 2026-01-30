"""
Fail Marker: Runs after a turn to scan for failures and mark nodes.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

Can be called manually or hooked into the engine's post-turn step.
Reads the turn's node results and marks 🔴 where things went wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .turn_cycle import TurnCycle, Node, NodeStatus, NodeType


@dataclass
class FailCriteria:
    """What counts as a failure for a node."""
    empty_result: bool = True         # node completed but produced nothing
    error_keywords: list[str] | None = None  # result contains these → fail
    status_check: bool = True         # node still PLANNED at end of turn → fail

    def __post_init__(self):
        if self.error_keywords is None:
            self.error_keywords = [
                "error", "failed", "exception", "timeout",
                "not found", "permission denied", "abort",
            ]


class FailMarker:
    """
    Post-turn scanner. Walks all nodes in a turn and marks failures
    based on criteria.
    """

    def __init__(self, criteria: FailCriteria | None = None):
        self.criteria = criteria or FailCriteria()
        self.report: list[dict[str, Any]] = []

    def scan_turn(self, cycle: TurnCycle, turn_number: int | None = None) -> list[dict[str, Any]]:
        """
        Scan a turn's nodes and mark failures.
        If turn_number is None, scans the current turn.
        Returns a report of what was marked.
        Post-execution sweep — runs after path completion check.
        """
        self.report = []

        if turn_number is not None:
            turns = [t for t in cycle.turns if t.number == turn_number]
            if not turns:
                return []
            turn = turns[0]
        else:
            turn = cycle.current_turn
            if not turn:
                return []

        for row in turn.rows:
            for node in row:
                self._check_node(node)
                for ext in node.extensions:
                    self._check_node(ext)

        return self.report

    def scan_all(self, cycle: TurnCycle) -> list[dict[str, Any]]:
        """Scan all turns in the cycle."""
        self.report = []
        for turn in cycle.turns:
            for row in turn.rows:
                for node in row:
                    self._check_node(node)
                    for ext in node.extensions:
                        self._check_node(ext)
        return self.report

    def _check_node(self, node: Node):
        """Check a single node against fail criteria."""
        reasons = []

        # Already marked failed — skip
        if node.status == NodeStatus.FAILED:
            return

        # Still planned at scan time — unused node
        if self.criteria.status_check and node.status == NodeStatus.PLANNED:
            reasons.append("node was never activated")

        # Completed but empty result
        if self.criteria.empty_result and node.status == NodeStatus.COMPLETED:
            if not node.result or not node.result.strip():
                reasons.append("completed with empty result")

        # Result contains error keywords
        if self.criteria.error_keywords and node.result:
            lower_result = node.result.lower()
            for kw in self.criteria.error_keywords:
                if kw in lower_result:
                    reasons.append(f"result contains '{kw}'")
                    break

        if reasons:
            node.mark_fail("; ".join(reasons))
            self.report.append({
                "node_id": node.id,
                "turn": node.turn,
                "row": node.row,
                "position": node.position,
                "original_type": node.type.value,
                "reasons": reasons,
            })


def mark_and_report(cycle: TurnCycle, turn_number: int | None = None) -> str:
    """Convenience: scan, mark, and return a readable report."""
    marker = FailMarker()
    failures = marker.scan_turn(cycle, turn_number)

    if not failures:
        return "No failures detected."

    lines = [f"Failures detected: {len(failures)}", ""]
    for f in failures:
        lines.append(f"  🔴 {f['node_id']}: {', '.join(f['reasons'])}")

    # Render the turn after marking
    turn = cycle.current_turn
    if turn:
        lines.append("")
        lines.append(turn.render())

    return "\n".join(lines)
