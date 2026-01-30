"""
Retrieval Index: Tag every consumed token chunk for fast filtering.

Five tag dimensions:
  - type:       source-code, config, test, docs, error-log, user-intent, tool-result
  - relevance:  critical, useful, ambient, noise
  - volatility: static, stale-risk, live, ephemeral
  - scope:      this-function, this-file, this-module, cross-module, whole-project, external-dep
  - trust:      verified, reported, inferred, stale
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TagType(Enum):
    SOURCE_CODE = "source-code"
    CONFIG = "config"
    TEST = "test"
    DOCS = "docs"
    ERROR_LOG = "error-log"
    USER_INTENT = "user-intent"
    TOOL_RESULT = "tool-result"


class TagRelevance(Enum):
    CRITICAL = "critical"      # blocks progress without it
    USEFUL = "useful"          # informs the approach
    AMBIENT = "ambient"        # nice to have
    NOISE = "noise"            # actively ignore


class TagVolatility(Enum):
    STATIC = "static"          # won't change (e.g. language spec)
    STALE_RISK = "stale-risk"  # may have changed since last read
    LIVE = "live"              # changes every run (e.g. test output)
    EPHEMERAL = "ephemeral"    # one-time value, don't cache


class TagScope(Enum):
    THIS_FUNCTION = "this-function"
    THIS_FILE = "this-file"
    THIS_MODULE = "this-module"
    CROSS_MODULE = "cross-module"
    WHOLE_PROJECT = "whole-project"
    EXTERNAL_DEP = "external-dep"


class TagTrust(Enum):
    VERIFIED = "verified"      # I read it myself
    REPORTED = "reported"      # user told me
    INFERRED = "inferred"      # I guessed from context
    STALE = "stale"            # read long ago, may be outdated


@dataclass
class Tag:
    type: TagType
    relevance: TagRelevance
    volatility: TagVolatility
    scope: TagScope
    trust: TagTrust


@dataclass
class TokenChunk:
    """A chunk of consumed tokens with its retrieval tags."""
    content: str
    source: str           # e.g. "auth.ts", "grep:handleError", "user message"
    token_count: int
    tag: Tag
    metadata: dict[str, Any] = field(default_factory=dict)


class RetrievalIndex:
    """
    Index over all consumed token chunks.
    Supports filtering by any combination of tag dimensions.
    """

    def __init__(self):
        self.chunks: list[TokenChunk] = []

    def index(self, chunk: TokenChunk):
        """Add a chunk to the index."""
        self.chunks.append(chunk)

    def index_raw(
        self,
        content: str,
        source: str,
        type: TagType,
        relevance: TagRelevance,
        volatility: TagVolatility,
        scope: TagScope,
        trust: TagTrust,
        metadata: dict[str, Any] | None = None,
    ) -> TokenChunk:
        """Convenience: create a chunk, tag it, and index it in one call."""
        chunk = TokenChunk(
            content=content,
            source=source,
            token_count=max(1, len(content) // 4),
            tag=Tag(
                type=type,
                relevance=relevance,
                volatility=volatility,
                scope=scope,
                trust=trust,
            ),
            metadata=metadata or {},
        )
        self.index(chunk)
        return chunk

    def query(
        self,
        type: TagType | None = None,
        relevance: TagRelevance | None = None,
        volatility: TagVolatility | None = None,
        scope: TagScope | None = None,
        trust: TagTrust | None = None,
    ) -> list[TokenChunk]:
        """Filter chunks by any combination of tag dimensions."""
        results = self.chunks
        if type is not None:
            results = [c for c in results if c.tag.type == type]
        if relevance is not None:
            results = [c for c in results if c.tag.relevance == relevance]
        if volatility is not None:
            results = [c for c in results if c.tag.volatility == volatility]
        if scope is not None:
            results = [c for c in results if c.tag.scope == scope]
        if trust is not None:
            results = [c for c in results if c.tag.trust == trust]
        return results

    def critical(self) -> list[TokenChunk]:
        """Shortcut: everything tagged as critical."""
        return self.query(relevance=TagRelevance.CRITICAL)

    def stale(self) -> list[TokenChunk]:
        """Shortcut: everything that might be outdated."""
        return [
            c for c in self.chunks
            if c.tag.trust == TagTrust.STALE or c.tag.volatility == TagVolatility.STALE_RISK
        ]

    def by_source(self, source: str) -> list[TokenChunk]:
        """Get all chunks from a specific source."""
        return [c for c in self.chunks if c.source == source]

    @property
    def total_tokens(self) -> int:
        return sum(c.token_count for c in self.chunks)

    def summary(self) -> dict[str, Any]:
        """Breakdown of indexed content by each dimension."""
        def count_by(attr: str) -> dict[str, int]:
            counts: dict[str, int] = {}
            for chunk in self.chunks:
                key = getattr(chunk.tag, attr).value
                counts[key] = counts.get(key, 0) + chunk.token_count
            return counts

        return {
            "total_chunks": len(self.chunks),
            "total_tokens": self.total_tokens,
            "by_type": count_by("type"),
            "by_relevance": count_by("relevance"),
            "by_volatility": count_by("volatility"),
            "by_scope": count_by("scope"),
            "by_trust": count_by("trust"),
        }

    def auto_tag(self, content: str, source: str) -> Tag:
        """
        Heuristic auto-tagger. Guesses tag values from content and source.
        Not perfect — meant as a starting point to be corrected.
        """
        # type
        if source.endswith((".py", ".ts", ".js", ".rs", ".go")):
            type_ = TagType.SOURCE_CODE
        elif source.endswith((".json", ".yaml", ".yml", ".toml", ".env")):
            type_ = TagType.CONFIG
        elif "test" in source.lower() or "spec" in source.lower():
            type_ = TagType.TEST
        elif source == "user":
            type_ = TagType.USER_INTENT
        else:
            type_ = TagType.TOOL_RESULT

        # relevance
        lower = content.lower()
        if "error" in lower or "fail" in lower or "assert" in lower:
            relevance = TagRelevance.CRITICAL
        elif "import" in lower or "def " in lower or "class " in lower:
            relevance = TagRelevance.USEFUL
        elif "todo" in lower or "fixme" in lower:
            relevance = TagRelevance.USEFUL
        else:
            relevance = TagRelevance.AMBIENT

        # volatility
        if source.endswith((".lock", ".sum")):
            volatility = TagVolatility.STATIC
        elif "test" in source.lower():
            volatility = TagVolatility.LIVE
        else:
            volatility = TagVolatility.STALE_RISK

        # scope — hard to guess, default to file
        scope = TagScope.THIS_FILE

        # trust
        trust = TagTrust.VERIFIED  # we're reading it ourselves

        return Tag(
            type=type_,
            relevance=relevance,
            volatility=volatility,
            scope=scope,
            trust=trust,
        )
