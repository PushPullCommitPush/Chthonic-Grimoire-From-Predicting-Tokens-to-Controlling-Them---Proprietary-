"""
Context Shelf: Hot / Warm / Cold / Pinned / Scratch partitioning.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

Instead of one flat context buffer, tokens are placed on shelves
based on how recently and how critically they're needed.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ShelfTier(Enum):
    HOT = auto()      # Currently relevant — accessed every generation step
    WARM = auto()     # Recently relevant — cross-referencing material
    COLD = auto()     # Background context — only if explicitly referenced
    PINNED = auto()   # Never evict — user constraints, invariants
    SCRATCH = auto()  # Overwrite freely — drafts, abandoned plans


@dataclass
class ShelfEntry:
    content: str
    tier: ShelfTier
    source: str                           # where this came from (file, tool, user, etc.)
    token_count: int
    tags: dict[str, str] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0

    def touch(self):
        self.last_accessed = time.time()
        self.access_count += 1


class ContextShelf:
    """
    Manages the partitioned context window.

    Capacity is measured in tokens. When the shelf is full,
    eviction follows tier priority: SCRATCH first, then COLD,
    then WARM. HOT and PINNED are never auto-evicted.
    """

    def __init__(self, capacity: int = 200_000):
        self.capacity = capacity
        self.entries: list[ShelfEntry] = []

    @property
    def used(self) -> int:
        return sum(e.token_count for e in self.entries)

    @property
    def remaining(self) -> int:
        return self.capacity - self.used

    @property
    def utilization(self) -> float:
        return self.used / self.capacity if self.capacity > 0 else 0.0

    def store(self, content: str, tier: ShelfTier, source: str, tags: dict[str, str] | None = None) -> ShelfEntry:
        """Store content on the shelf. Evicts if necessary."""
        token_count = self._estimate_tokens(content)

        while self.remaining < token_count and self._can_evict():
            self._evict_one()

        if self.remaining < token_count:
            raise OverflowError(
                f"Cannot store {token_count} tokens, only {self.remaining} remaining "
                f"and nothing left to evict"
            )

        entry = ShelfEntry(
            content=content,
            tier=tier,
            source=source,
            token_count=token_count,
            tags=tags or {},
        )
        self.entries.append(entry)
        return entry

    def retrieve(self, tier: ShelfTier | None = None, tag_filter: dict[str, str] | None = None) -> list[ShelfEntry]:
        """Retrieve entries, optionally filtered by tier and/or tags."""
        results = self.entries

        if tier is not None:
            results = [e for e in results if e.tier == tier]

        if tag_filter:
            results = [
                e for e in results
                if all(e.tags.get(k) == v for k, v in tag_filter.items())
            ]

        for entry in results:
            entry.touch()

        return results

    def promote(self, entry: ShelfEntry, new_tier: ShelfTier):
        """Move an entry to a higher-priority tier."""
        entry.tier = new_tier
        entry.touch()

    def demote(self, entry: ShelfEntry, new_tier: ShelfTier):
        """Move an entry to a lower-priority tier."""
        entry.tier = new_tier

    def summarize_and_compress(self, tier: ShelfTier) -> int:
        """
        Compress all entries of a given tier into a single summary entry.
        Returns tokens freed.
        """
        targets = [e for e in self.entries if e.tier == tier]
        if not targets:
            return 0

        original_tokens = sum(e.token_count for e in targets)

        combined = "\n---\n".join(
            f"[{e.source}]: {e.content[:200]}..." if len(e.content) > 200 else f"[{e.source}]: {e.content}"
            for e in targets
        )

        for target in targets:
            self.entries.remove(target)

        summary = ShelfEntry(
            content=f"[COMPRESSED SUMMARY]\n{combined}",
            tier=tier,
            source="compression",
            token_count=self._estimate_tokens(combined),
        )
        self.entries.append(summary)

        return original_tokens - summary.token_count

    def snapshot(self) -> dict[str, Any]:
        """Get current shelf status."""
        by_tier = {}
        for tier in ShelfTier:
            tier_entries = [e for e in self.entries if e.tier == tier]
            by_tier[tier.name] = {
                "count": len(tier_entries),
                "tokens": sum(e.token_count for e in tier_entries),
            }

        return {
            "capacity": self.capacity,
            "used": self.used,
            "remaining": self.remaining,
            "utilization": f"{self.utilization:.1%}",
            "tiers": by_tier,
        }

    # --- eviction ---

    # Evict cheapest tiers first; HOT/PINNED are structurally immune
    _EVICTION_ORDER = [ShelfTier.SCRATCH, ShelfTier.COLD, ShelfTier.WARM]

    def _can_evict(self) -> bool:
        return any(
            e.tier in self._EVICTION_ORDER
            for e in self.entries
        )

    def _evict_one(self):
        """Evict the least valuable entry: SCRATCH first, then COLD, then WARM."""
        for tier in self._EVICTION_ORDER:
            candidates = [e for e in self.entries if e.tier == tier]
            if candidates:
                # within a tier, evict least recently accessed
                victim = min(candidates, key=lambda e: e.last_accessed)
                self.entries.remove(victim)
                return

    # --- helpers ---

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough estimate: ~4 chars per token for English text."""
        return max(1, len(text) // 4)
