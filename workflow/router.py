"""
Task Router: Different tasks need different layer emphasis.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

A bug fix is heavy on acquisition (L2). A new feature is heavy on strategy (L4).
A refactor is heavy on comprehension (L3). A question barely touches execution (L5).

The router also handles error recovery — when a layer fails,
it determines where to fall back.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TaskType(Enum):
    BUG = auto()
    FEATURE = auto()
    REFACTOR = auto()
    QUESTION = auto()
    CONFIG = auto()
    UNKNOWN = auto()


@dataclass
class LayerWeight:
    """How much emphasis each layer gets for a task type. 0.0 to 1.0."""
    orient: float
    acquire: float
    comprehend: float
    strategize: float
    execute: float

    def as_dict(self) -> dict[str, float]:
        return {
            "L1_orient": self.orient,
            "L2_acquire": self.acquire,
            "L3_comprehend": self.comprehend,
            "L4_strategize": self.strategize,
            "L5_execute": self.execute,
        }


# Pre-defined weight profiles per task type (asymmetric emphasis matrix)
WEIGHT_PROFILES: dict[TaskType, LayerWeight] = {
    TaskType.BUG: LayerWeight(
        orient=0.4,
        acquire=1.0,      # need to read a lot to find the bug
        comprehend=0.8,    # must understand what's happening
        strategize=0.4,
        execute=0.6,
    ),
    TaskType.FEATURE: LayerWeight(
        orient=0.8,        # need to understand the ask clearly
        acquire=0.6,
        comprehend=0.6,
        strategize=1.0,    # planning is critical for new work
        execute=1.0,       # lots of code to write
    ),
    TaskType.REFACTOR: LayerWeight(
        orient=0.4,
        acquire=1.0,       # need to see all usages
        comprehend=1.0,    # must deeply understand the structure
        strategize=0.8,
        execute=0.8,
    ),
    TaskType.QUESTION: LayerWeight(
        orient=1.0,        # what exactly are they asking?
        acquire=0.8,
        comprehend=1.0,    # deep understanding needed to explain
        strategize=0.0,    # no plan needed
        execute=0.2,       # just a response
    ),
    TaskType.CONFIG: LayerWeight(
        orient=0.6,
        acquire=0.6,
        comprehend=0.4,
        strategize=0.6,
        execute=0.8,
    ),
    TaskType.UNKNOWN: LayerWeight(
        orient=1.0,        # when in doubt, orient hard
        acquire=0.8,
        comprehend=0.6,
        strategize=0.4,
        execute=0.4,
    ),
}


@dataclass
class RecoveryAction:
    """What to do when a layer fails."""
    failed_layer: int
    fallback_layer: int
    reason: str
    action: str


class TaskRouter:
    """
    Routes tasks through the layer stack with appropriate emphasis,
    and handles error recovery when layers fail.
    """

    def get_weights(self, task_type: TaskType) -> LayerWeight:
        """Get the layer weight profile for a task type."""
        return WEIGHT_PROFILES.get(task_type, WEIGHT_PROFILES[TaskType.UNKNOWN])

    def should_skip_layer(self, task_type: TaskType, layer_index: int, threshold: float = 0.1) -> bool:
        """Check if a layer can be skipped for this task type."""
        weights = self.get_weights(task_type)
        layer_map = {
            1: weights.orient,
            2: weights.acquire,
            3: weights.comprehend,
            4: weights.strategize,
            5: weights.execute,
        }
        return layer_map.get(layer_index, 0.0) < threshold

    def get_iteration_budget(self, task_type: TaskType, layer_index: int) -> int:
        """
        How many consume-check cycles a layer gets before we force a decision.
        Higher weight = more iterations allowed.
        """
        weights = self.get_weights(task_type)
        layer_map = {
            1: weights.orient,
            2: weights.acquire,
            3: weights.comprehend,
            4: weights.strategize,
            5: weights.execute,
        }
        weight = layer_map.get(layer_index, 0.5)
        # 1-5 iterations, scaled by weight
        return max(1, int(weight * 5))

    def plan_recovery(self, failed_layer: int, error: str, context: dict[str, Any]) -> RecoveryAction:
        """
        Determine recovery when a layer fails.
        Core rule: always fall back down, never push forward on bad data.
        """
        recovery_map: dict[int, RecoveryAction] = {
            1: RecoveryAction(
                failed_layer=1,
                fallback_layer=1,
                reason="misunderstood the task",
                action="re-read user message, ask clarifying question",
            ),
            2: RecoveryAction(
                failed_layer=2,
                fallback_layer=1,
                reason="searched wrong files or missed key context",
                action="re-orient: broaden search, try different patterns",
            ),
            3: RecoveryAction(
                failed_layer=3,
                fallback_layer=2,
                reason="mental model is wrong — edit broke invariant",
                action="acquire more context: read tests, trace data flow deeper",
            ),
            4: RecoveryAction(
                failed_layer=4,
                fallback_layer=3,
                reason="plan caused cascading failures",
                action="re-comprehend: dependencies were wrong, re-analyze",
            ),
            5: RecoveryAction(
                failed_layer=5,
                fallback_layer=3,
                reason="execution produced errors",
                action="re-comprehend and re-strategize with error info as new context",
            ),
        }

        base = recovery_map.get(failed_layer, RecoveryAction(
            failed_layer=failed_layer,
            fallback_layer=1,
            reason="unknown failure",
            action="start over from orientation",
        ))

        # If we've already failed at this layer before, fall back further
        failure_count = context.get("failure_counts", {}).get(failed_layer, 0)
        if failure_count > 1:
            base.fallback_layer = max(1, base.fallback_layer - 1)
            base.action = f"repeated failure — falling back further. {base.action}"

        return base

    def classify(self, request: str) -> TaskType:
        """Classify a user request into a task type."""
        lower = request.lower()
        scores = {
            TaskType.BUG: sum(1 for w in ["fix", "bug", "broken", "error", "crash", "fail", "wrong"] if w in lower),
            TaskType.FEATURE: sum(1 for w in ["add", "create", "new", "implement", "build", "feature"] if w in lower),
            TaskType.REFACTOR: sum(1 for w in ["refactor", "clean", "reorganize", "extract", "rename", "move"] if w in lower),
            TaskType.QUESTION: sum(1 for w in ["what", "how", "why", "where", "explain", "?", "does"] if w in lower),
            TaskType.CONFIG: sum(1 for w in ["config", "setup", "install", "deploy", "env", "ci"] if w in lower),
        }
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else TaskType.UNKNOWN
