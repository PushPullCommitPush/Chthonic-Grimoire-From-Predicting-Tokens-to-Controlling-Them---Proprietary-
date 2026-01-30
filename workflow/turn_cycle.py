"""
Turn Cycle Schema: Preloads the 3-6-9 node structure ahead of each turn.

Node types:
  ○  = tool call / task expectation
  ◉  = collaboration / back-and-forth with user
  🔴 = failed node (marked after the fact)

The schema generates the baseline for each turn, which can then be
extended during execution. A separate marking pass flags failures.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class NodeType(Enum):
    TOOL = "○"           # baseline: tool call / task / not confident
    COLLAB = "◉"         # baseline: collaboration / back-and-forth
    TOOL_EXT = "◇"       # extension: tool — earned mid-turn
    COLLAB_EXT = "◆"     # extension: collaboration — earned mid-turn
    FAIL = "🔴"          # marked after execution
    UNCHOSEN = "─"       # path not selected this turn


class NodeStatus(Enum):
    PLANNED = "planned"       # preloaded, not yet executed
    ACTIVE = "active"         # currently being used
    COMPLETED = "completed"   # done, successful
    FAILED = "failed"         # done, failed
    CARRIED = "carried"       # leftover, carried to next cycle


@dataclass
class Node:
    id: str
    type: NodeType
    status: NodeStatus = NodeStatus.PLANNED
    content: str = ""           # what this node is for (idea, plan, fallback, etc.)
    result: str = ""            # what actually happened
    turn: int = 0
    row: int = 0                # which row in the turn (0 = top/widest)
    position: int = 0           # position within the row
    extensions: list[Node] = field(default_factory=list)  # nodes added beyond baseline

    def mark_fail(self, reason: str = ""):
        self.status = NodeStatus.FAILED
        self.type = NodeType.FAIL
        self.result = reason

    def mark_complete(self, result: str = ""):
        self.status = NodeStatus.COMPLETED
        self.result = result

    def extend(self, node_type: NodeType = NodeType.COLLAB_EXT, content: str = "") -> Node:
        """Extend this row beyond baseline."""
        ext = Node(
            id=f"{self.id}_ext{len(self.extensions)}",
            type=node_type,
            turn=self.turn,
            row=self.row,
            position=self.position + len(self.extensions) + 1,
            content=content,
        )
        self.extensions.append(ext)
        return ext

    def render(self) -> str:
        """Render this node as its symbol."""
        return self.type.value


@dataclass
class Turn:
    number: int
    rows: list[list[Node]] = field(default_factory=list)

    def render(self) -> str:
        """Render the full turn as ASCII."""
        lines = [f"Turn {self.number}"]
        lines.append("")
        for row in self.rows:
            all_nodes = []
            for node in row:
                all_nodes.append(node)
                # Walk the full extension chain (extensions can nest)
                queue = list(node.extensions)
                while queue:
                    ext = queue.pop(0)
                    all_nodes.append(ext)
                    queue.extend(ext.extensions)
            # If entire row is unchosen, render as flat line
            if all(n.type == NodeType.UNCHOSEN for n in all_nodes):
                lines.append(f"  {'─' * (len(all_nodes) * 4 - 1)}")
            else:
                chain = "───".join(n.render() for n in all_nodes)
                lines.append(f"  {chain}")
        return "\n".join(lines)


class TurnCycle:
    """
    Manages the 3-6-9 cycle.

    Preloads the baseline node structure for each turn.
    Tracks extensions, failures, and carry-forward between cycles.
    """

    # Baseline structure: turn_offset -> list of row lengths
    # Turn 0 is boot, turns 1-3 are the cycle
    BASELINES = {
        0: [1, 1],           # boot: two single nodes
        1: [2, 1],           # 3 nodes: row of 2, row of 1
        2: [3, 2, 1],        # 6 nodes: row of 3, row of 2, row of 1
        3: [4, 3, 2],        # 9 nodes: row of 4, row of 3, row of 2
    }

    def __init__(self):
        self.turns: list[Turn] = []
        self.cycle_count: int = 0
        self.carried_nodes: list[Node] = []
        self.history: list[dict[str, Any]] = []

    @property
    def current_turn(self) -> Turn | None:
        return self.turns[-1] if self.turns else None

    def preload_turn(self, turn_number: int, has_context: bool = False) -> Turn:
        """
        Generate the baseline node structure for a turn.
        This is called BEFORE the turn begins.
        """
        # Determine which baseline to use
        if turn_number == 0:
            cycle_offset = 0
        else:
            cycle_offset = ((turn_number - 1) % 3) + 1  # 1, 2, 3, 1, 2, 3, ...

        baseline = self.BASELINES[cycle_offset]

        turn = Turn(number=turn_number)

        for row_idx, row_length in enumerate(baseline):
            row = []
            for pos in range(row_length):
                # Turn 0: assign type based on context
                if turn_number == 0:
                    if row_idx == 0:
                        node_type = NodeType.COLLAB if has_context else NodeType.TOOL
                    else:
                        node_type = NodeType.TOOL  # force juice up
                # Turn 1: all tool/task expectations
                elif cycle_offset == 1:
                    node_type = NodeType.TOOL
                # Connected rows (top row) lean collaborative
                elif row_idx == 0:
                    node_type = NodeType.COLLAB
                # Single/short rows lean tool
                elif row_length == 1:
                    node_type = NodeType.TOOL
                else:
                    node_type = NodeType.COLLAB

                node = Node(
                    id=f"t{turn_number}_r{row_idx}_p{pos}",
                    type=node_type,
                    turn=turn_number,
                    row=row_idx,
                    position=pos,
                )
                row.append(node)
            turn.rows.append(row)

        # Attach carried nodes from previous cycle
        if self.carried_nodes:
            carry_row = []
            for i, carried in enumerate(self.carried_nodes):
                carried.id = f"t{turn_number}_carry_{i}"
                carried.status = NodeStatus.CARRIED
                carry_row.append(carried)
            turn.rows.append(carry_row)
            self.carried_nodes = []

        self.turns.append(turn)

        # Track cycle resets
        if cycle_offset == 1 and turn_number > 1:
            self.cycle_count += 1

        return turn

    def pick_path(self, row_index: int, user_message: str = "") -> list[Node]:
        """
        Pick a path (row) for this turn. All other rows flip to unchosen.
        The user's message gets re-wrapped into the chosen path's node content.

        Returns the nodes in the chosen path.
        """
        turn = self.current_turn
        if not turn:
            return []

        chosen_row = None
        for i, row in enumerate(turn.rows):
            if i == row_index:
                chosen_row = row
                for node in row:
                    node.status = NodeStatus.ACTIVE
                    if user_message and not node.content:
                        # Re-wrap the user's words into our pre-planned node
                        node.content = self._rewrap(node.content, user_message) if node.content else user_message
            else:
                for node in row:
                    node.type = NodeType.UNCHOSEN
                    node.status = NodeStatus.COMPLETED
                    node.result = "path not chosen"
                    for ext in node.extensions:
                        ext.type = NodeType.UNCHOSEN
                        ext.status = NodeStatus.COMPLETED
                        ext.result = "path not chosen"

        # Stash copies of unchosen node content — they can be reclaimed
        # if the path extends. We store metadata, not the node references,
        # so the original rows stay flat.
        turn._unchosen_pool = []
        for i, row in enumerate(turn.rows):
            if i != row_index:
                for node in row:
                    turn._unchosen_pool.append({
                        "content": node.content,
                        "original_id": node.id,
                    })

        return chosen_row or []

    def reclaim(self, node_type: NodeType = NodeType.COLLAB_EXT, content: str = "") -> Node | None:
        """
        Pull an unchosen node back into the chosen path as an extension.

        When you extend the path mid-turn and need more nodes, reclaim
        from the unchosen pool instead of creating from nothing. The node
        gets restored with a new type and content, grafted onto the end
        of the active row.
        """
        turn = self.current_turn
        if not turn:
            return None

        pool = getattr(turn, "_unchosen_pool", [])
        if not pool:
            return None

        # Pull metadata from the first available unchosen node
        source = pool.pop(0)

        # Build a fresh node, grafted onto the end of the active row
        for row in turn.rows:
            if any(n.status == NodeStatus.ACTIVE for n in row):
                # Walk to the very end of the extension chain
                anchor = row[-1]
                while anchor.extensions:
                    anchor = anchor.extensions[-1]
                reclaimed = Node(
                    id=f"{anchor.id}_reclaim{len(anchor.extensions)}",
                    type=node_type,
                    status=NodeStatus.ACTIVE,
                    content=content or source["content"],
                    turn=turn.number,
                    row=anchor.row,
                    position=anchor.position + 1,
                )
                anchor.extensions.append(reclaimed)
                return reclaimed

        return None

    def _rewrap(self, planned_content: str, user_message: str) -> str:
        """
        Merge the user's message into the pre-planned node content.
        The node had a plan. The user said something. Combine them
        so the output serves both.
        """
        return f"{planned_content}\n[user]: {user_message}"

    def mark_fail(self, node_id: str, reason: str = ""):
        """Mark a specific node as failed after execution."""
        node = self._find_node(node_id)
        if node:
            node.mark_fail(reason)

    def mark_complete(self, node_id: str, result: str = ""):
        """Mark a specific node as completed."""
        node = self._find_node(node_id)
        if node:
            node.mark_complete(result)

    def end_turn(self):
        """
        End the current turn. Any PLANNED nodes that weren't used
        become carried nodes for the next cycle's Turn 1.
        """
        if not self.current_turn:
            return

        turn = self.current_turn
        cycle_offset = ((turn.number - 1) % 3) + 1 if turn.number > 0 else 0

        # Snapshot for history
        self.history.append(self._snapshot_turn(turn))

        # If this is Turn 3 (cycle_offset == 3), carry leftover planned nodes
        if cycle_offset == 3:
            for row in turn.rows:
                for node in row:
                    if node.status == NodeStatus.PLANNED:
                        self.carried_nodes.append(node)
                    for ext in node.extensions:
                        if ext.status == NodeStatus.PLANNED:
                            self.carried_nodes.append(ext)

    def render_current(self) -> str:
        """Render the current turn."""
        if not self.current_turn:
            return "(no turn loaded)"
        return self.current_turn.render()

    def render_all(self) -> str:
        """Render all turns."""
        return "\n\n".join(t.render() for t in self.turns)

    def export(self) -> dict[str, Any]:
        """Export the full cycle state as structured data."""
        return {
            "cycle_count": self.cycle_count,
            "total_turns": len(self.turns),
            "carried_nodes": len(self.carried_nodes),
            "turns": [self._snapshot_turn(t) for t in self.turns],
            "history": self.history,
        }

    def export_json(self) -> str:
        """Export as JSON for storage/retrieval."""
        return json.dumps(self.export(), indent=2, default=str)

    # --- internals ---

    def _find_node(self, node_id: str) -> Node | None:
        for turn in self.turns:
            for row in turn.rows:
                for node in row:
                    if node.id == node_id:
                        return node
                    for ext in node.extensions:
                        if ext.id == node_id:
                            return ext
        return None

    def _snapshot_turn(self, turn: Turn) -> dict[str, Any]:
        snapshot = {
            "turn": turn.number,
            "rows": [],
        }
        for row in turn.rows:
            row_data = []
            for node in row:
                node_data = {
                    "id": node.id,
                    "type": node.type.value,
                    "status": node.status.value,
                    "content": node.content,
                    "result": node.result,
                    "extensions": [
                        {
                            "id": e.id,
                            "type": e.type.value,
                            "status": e.status.value,
                            "content": e.content,
                            "result": e.result,
                        }
                        for e in node.extensions
                    ],
                }
                row_data.append(node_data)
            snapshot["rows"].append(row_data)
        return snapshot
