"""
Workflow Engine: Ties the layers, shelf, index, and router together.

This is the main loop. It:
1. Orients on the task
2. Acquires context (consuming tokens onto the shelf)
3. Builds comprehension (tagging chunks in the index)
4. Strategizes (plans the work)
5. Executes (produces output)

At every step, it checks: do I know enough? If not, loop back.
If a layer fails, the router decides where to fall back.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from .layers import (
    Layer,
    LayerResult,
    LayerStatus,
    Orient,
    Acquire,
    Comprehend,
    Strategize,
    Execute,
)
from .context_shelf import ContextShelf, ShelfTier
from .retrieval_index import RetrievalIndex
from .router import TaskRouter, TaskType

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
    """Tuning knobs for the engine."""
    max_total_iterations: int = 20        # hard stop to prevent infinite loops
    max_layer_retries: int = 3            # per-layer retry limit
    context_capacity: int = 200_000       # token budget
    auto_compress_at: float = 0.85        # compress cold shelf at this utilization


@dataclass
class Turn:
    """One complete cycle through the engine."""
    layer_name: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
    fallback: int | None = None


class WorkflowEngine:
    """
    The main engine. Feed it a user request and it walks the stack.
    """

    def __init__(self, config: EngineConfig | None = None):
        self.config = config or EngineConfig()
        self.shelf = ContextShelf(capacity=self.config.context_capacity)
        self.index = RetrievalIndex()
        self.router = TaskRouter()

        self.layers: list[Layer] = [
            Orient(),
            Acquire(),
            Comprehend(),
            Strategize(),
            Execute(),
        ]

        self.context: dict[str, Any] = {}
        self.history: list[Turn] = []
        self.failure_counts: dict[int, int] = {}

    def run(self, user_request: str) -> dict[str, Any]:
        """
        Main entry point. Process a user request through all layers.
        Returns the final context with execution results.
        """
        self.context["user_request"] = user_request
        self.context["failure_counts"] = self.failure_counts

        # Store the user request on the hot shelf
        self.shelf.store(
            content=user_request,
            tier=ShelfTier.PINNED,
            source="user",
            tags={"type": "user-intent"},
        )

        # Classify the task
        task_type = self.router.classify(user_request)
        self.context["task_type"] = task_type.name.lower()
        weights = self.router.get_weights(task_type)

        logger.info(f"Task classified as: {task_type.name}")
        logger.info(f"Layer weights: {weights.as_dict()}")

        # Walk the layer stack
        current_layer_idx = 0
        total_iterations = 0

        while current_layer_idx < len(self.layers):
            if total_iterations >= self.config.max_total_iterations:
                logger.warning("Hit max iterations, forcing completion")
                break

            layer = self.layers[current_layer_idx]
            total_iterations += 1

            # Check if this layer should be skipped
            if self.router.should_skip_layer(task_type, layer.index):
                logger.info(f"Skipping {layer.name} (low weight for {task_type.name})")
                current_layer_idx += 1
                continue

            logger.info(f"Running layer: {layer.name} (iteration {total_iterations})")

            # Run the layer
            result = layer.run(self.context)

            # Record the turn
            turn = Turn(
                layer_name=layer.name,
                status=result.status.name,
                output=result.output,
                gaps=result.gaps,
                fallback=result.fallback_to,
            )
            self.history.append(turn)

            if result.status == LayerStatus.SATISFIED:
                # Merge output into context
                self.context.update(result.output)
                # Store layer output on the shelf
                self._shelf_layer_output(layer, result)
                # Advance to next layer
                current_layer_idx += 1

            elif result.status == LayerStatus.FAILED:
                # Track failure count
                self.failure_counts[layer.index] = self.failure_counts.get(layer.index, 0) + 1

                if self.failure_counts[layer.index] >= self.config.max_layer_retries:
                    logger.error(f"Layer {layer.name} failed {self.config.max_layer_retries} times, aborting")
                    self.context["aborted_at"] = layer.name
                    self.context["abort_reason"] = result.gaps
                    break

                # Get recovery action
                recovery = self.router.plan_recovery(
                    failed_layer=layer.index,
                    error="; ".join(result.gaps),
                    context=self.context,
                )
                logger.info(f"Recovery: {recovery.action}")

                # Fall back to the specified layer
                fallback_idx = recovery.fallback_layer - 1  # convert to 0-indexed
                current_layer_idx = max(0, fallback_idx)

                # Merge any partial output (might be useful for the fallback)
                if result.output:
                    self.context.update(result.output)

            # Auto-compress if shelf is getting full
            if self.shelf.utilization >= self.config.auto_compress_at:
                freed = self.shelf.summarize_and_compress(ShelfTier.COLD)
                logger.info(f"Auto-compressed cold shelf, freed {freed} tokens")

        return self.results()

    def results(self) -> dict[str, Any]:
        """Package the final results."""
        return {
            "context": {
                k: v for k, v in self.context.items()
                if k not in ("failure_counts",)
            },
            "history": [
                {
                    "layer": t.layer_name,
                    "status": t.status,
                    "gaps": t.gaps,
                }
                for t in self.history
            ],
            "shelf": self.shelf.snapshot(),
            "index": self.index.summary(),
            "failure_counts": dict(self.failure_counts),
        }

    def _shelf_layer_output(self, layer: Layer, result: LayerResult):
        """Store a layer's output on the appropriate shelf tier."""
        content = str(result.output)
        tier_map = {
            "orient": ShelfTier.HOT,
            "acquire": ShelfTier.WARM,
            "comprehend": ShelfTier.HOT,
            "strategize": ShelfTier.HOT,
            "execute": ShelfTier.WARM,
        }
        tier = tier_map.get(layer.name, ShelfTier.WARM)

        self.shelf.store(
            content=content,
            tier=tier,
            source=f"layer:{layer.name}",
            tags={"layer": layer.name},
        )

    def feed_context(self, content: str, source: str, tier: ShelfTier = ShelfTier.WARM):
        """
        Manually feed consumed tokens into the engine.
        Use this to provide file contents, tool results, etc.
        """
        entry = self.shelf.store(
            content=content,
            tier=tier,
            source=source,
        )

        tag = self.index.auto_tag(content, source)
        self.index.index_raw(
            content=content,
            source=source,
            type=tag.type,
            relevance=tag.relevance,
            volatility=tag.volatility,
            scope=tag.scope,
            trust=tag.trust,
        )

        # Also make it available in the flat context under acquired_content
        acquired = self.context.setdefault("acquired_content", {})
        acquired[source] = content

        return entry
