"""
Boot Loader: Seeds Turn 0 using stored run history.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

At boot, before the first turn begins, the BootLoader queries the RunLog
to determine:
  1. Whether to boot with context (has_context=True) or cold (force tool call)
  2. What to preload onto the context shelf
  3. How to bias node types for the first cycle

Scoring: each prior node/signal is ranked by
    score = recency + relevance - fail_penalty

The highest-scoring items get loaded into the hot shelf.
Everything else stays cold or gets dropped.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .run_log import RunLog, RunEntry
from .context_shelf import ContextShelf, ShelfTier


@dataclass
class BootContext:
    """What the BootLoader decided to surface at Turn 0."""
    has_context: bool                        # True = boot with context, False = cold boot (tool call)
    hot_items: list[dict[str, Any]]          # loaded into HOT shelf
    warm_items: list[dict[str, Any]]         # loaded into WARM shelf
    suggested_path_type: str                 # "tool" or "collab" — hint for preload_turn
    unfinished: list[str]                    # carried over from prior runs
    dormant_ideas: list[str]                 # unused 🟢 nodes from prior runs
    avoid_patterns: list[str]               # fail patterns to steer away from
    boot_reason: str                         # why we chose this boot config


class BootLoader:
    """
    Queries the RunLog and assembles a BootContext for Turn 0.

    Call boot() at the start of a new session. It returns a BootContext
    that tells the TurnCycle how to initialize and what to put on the shelf.
    """

    # Weights for scoring
    RECENCY_WEIGHT = 1.0       # more recent = higher
    RELEVANCE_WEIGHT = 2.0     # unfinished work = strong pull
    FAIL_PENALTY = 1.5         # repeated failures = avoid
    EMERGENCE_BONUS = 1.8      # unused ideas = high value

    # Thresholds — calibrated for Trident-9 cycle geometry
    CONTEXT_THRESHOLD = 0.3    # minimum score to boot with context
    HOT_LIMIT = 5              # max items in hot shelf at boot
    WARM_LIMIT = 10            # max items in warm shelf at boot

    def __init__(self, run_log: RunLog, shelf: ContextShelf | None = None):
        self.run_log = run_log
        self.shelf = shelf

    def boot(self) -> BootContext:
        """
        Main entry point. Analyze run history and decide how to boot.
        """
        if not self.run_log.entries:
            return self._cold_boot("no prior runs")

        scored = self._score_entries()

        if not scored:
            return self._cold_boot("no scoreable entries")

        top_score = scored[0]["score"]

        if top_score < self.CONTEXT_THRESHOLD:
            return self._cold_boot(f"top score {top_score:.2f} below threshold {self.CONTEXT_THRESHOLD}")

        return self._context_boot(scored)

    def _cold_boot(self, reason: str) -> BootContext:
        """No useful prior context. Force tool call at Turn 0."""
        return BootContext(
            has_context=False,
            hot_items=[],
            warm_items=[],
            suggested_path_type="tool",
            unfinished=[],
            dormant_ideas=[],
            avoid_patterns=[],
            boot_reason=f"cold boot: {reason}",
        )

    def _context_boot(self, scored: list[dict[str, Any]]) -> BootContext:
        """Prior context available. Load the best items onto the shelf."""
        hot_items = []
        warm_items = []

        for item in scored:
            entry = {
                "source": item["source"],
                "content": item["content"],
                "score": item["score"],
                "type": item["type"],
            }
            if len(hot_items) < self.HOT_LIMIT and item["score"] >= self.CONTEXT_THRESHOLD * 2:
                hot_items.append(entry)
            elif len(warm_items) < self.WARM_LIMIT:
                warm_items.append(entry)

        # Load onto the actual shelf if one is provided
        if self.shelf:
            for item in hot_items:
                self.shelf.store(
                    content=item["content"],
                    tier=ShelfTier.HOT,
                    source=item["source"],
                    tags={"boot": "true", "type": item["type"]},
                )
            for item in warm_items:
                self.shelf.store(
                    content=item["content"],
                    tier=ShelfTier.WARM,
                    source=item["source"],
                    tags={"boot": "true", "type": item["type"]},
                )

        # Collect avoidance patterns
        fail_freq = self.run_log.fail_frequency()
        avoid = [pattern for pattern, count in fail_freq.items() if count >= 2]

        # Collect unfinished and dormant
        unfinished = self.run_log.all_unfinished_content()[:self.HOT_LIMIT]
        dormant = self.run_log.all_unused_emergence()[:self.HOT_LIMIT]

        return BootContext(
            has_context=True,
            hot_items=hot_items,
            warm_items=warm_items,
            suggested_path_type=self.run_log.dominant_style(),
            unfinished=unfinished,
            dormant_ideas=dormant,
            avoid_patterns=avoid,
            boot_reason=f"context boot: {len(hot_items)} hot, {len(warm_items)} warm",
        )

    def _score_entries(self) -> list[dict[str, Any]]:
        """
        Score all retrievable items from the run log.

        Items are individual signals extracted from runs:
        - Unfinished content (high relevance)
        - Unused emergence (high emergence bonus)
        - User topics (moderate relevance)
        - Fail patterns (negative score — used for avoidance)

        Each item gets: recency + relevance - fail_penalty
        """
        now = time.time()
        items: list[dict[str, Any]] = []
        fail_freq = self.run_log.fail_frequency()

        for entry in self.run_log.entries:
            age_hours = (now - entry.timestamp) / 3600
            recency = self.RECENCY_WEIGHT / (1 + age_hours)  # decays over hours

            # Unfinished work — strongest signal
            for content in entry.unfinished_content:
                fail_count = sum(1 for p in entry.fail_patterns if p in content)
                score = recency + self.RELEVANCE_WEIGHT - (fail_count * self.FAIL_PENALTY)
                items.append({
                    "source": entry.run_id,
                    "content": content,
                    "score": score,
                    "type": "unfinished",
                })

            # Unused emergence — dormant value
            for content in entry.emerged_unused:
                score = recency + self.EMERGENCE_BONUS
                items.append({
                    "source": entry.run_id,
                    "content": content,
                    "score": score,
                    "type": "emergence",
                })

            # User topics — moderate pull
            for topic in entry.user_topics:
                score = recency + (self.RELEVANCE_WEIGHT * 0.5)
                items.append({
                    "source": entry.run_id,
                    "content": topic,
                    "score": score,
                    "type": "topic",
                })

            # Completed nodes with results — low-priority context
            # (already done, but may inform future decisions)
            if entry.completed_nodes > 0:
                summary = (
                    f"Completed {entry.completed_nodes}/{entry.total_nodes} nodes, "
                    f"{entry.failed_nodes} failed, style={entry.dominant_path_type}"
                )
                score = recency * 0.5  # half weight — it's background info
                items.append({
                    "source": entry.run_id,
                    "content": summary,
                    "score": score,
                    "type": "summary",
                })

        # Sort by score descending
        items.sort(key=lambda x: x["score"], reverse=True)
        return items

    def preview(self) -> dict[str, Any]:
        """
        Preview what the boot loader would do without actually loading.
        Useful for debugging or displaying boot decisions.
        """
        ctx = self.boot()
        return {
            "has_context": ctx.has_context,
            "boot_reason": ctx.boot_reason,
            "suggested_path_type": ctx.suggested_path_type,
            "hot_count": len(ctx.hot_items),
            "warm_count": len(ctx.warm_items),
            "unfinished_count": len(ctx.unfinished),
            "dormant_ideas_count": len(ctx.dormant_ideas),
            "avoid_patterns": ctx.avoid_patterns,
        }
