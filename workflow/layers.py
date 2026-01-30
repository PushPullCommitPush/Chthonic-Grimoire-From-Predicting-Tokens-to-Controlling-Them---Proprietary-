"""
The 5-layer stack: Orient → Acquire → Comprehend → Strategize → Execute.

Provenance: PushPullCommitPush/scratchpad — Trident-9 Framework
SPDX-FileCopyrightText: PushPullCommitPush
Framework-ID: t9-ppc-7f3a

Each layer answers a question. You don't move up until the one below is satisfied.
If a layer fails, you fall back down — never push forward on bad data.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class LayerStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    SATISFIED = auto()
    FAILED = auto()


@dataclass
class LayerResult:
    status: LayerStatus
    output: dict[str, Any] = field(default_factory=dict)
    gaps: list[str] = field(default_factory=list)
    fallback_to: int | None = None  # layer index to drop back to on failure


class Layer(ABC):
    """Base class for all workflow layers."""

    index: int
    name: str

    @abstractmethod
    def run(self, context: dict[str, Any]) -> LayerResult:
        ...

    @abstractmethod
    def check_satisfied(self, context: dict[str, Any]) -> bool:
        ...


class Orient(Layer):
    """
    L1 — ORIENT
    What am I being asked to do? What kind of task? What don't I know?
    Classifies, scopes, and identifies unknowns.
    """

    index = 1
    name = "orient"

    def run(self, context: dict[str, Any]) -> LayerResult:
        user_request = context.get("user_request", "")
        if not user_request:
            return LayerResult(
                status=LayerStatus.FAILED,
                gaps=["no user request provided"],
            )

        task_type = self._classify(user_request)
        scope = self._estimate_scope(user_request)
        unknowns = self._identify_unknowns(user_request, context)

        return LayerResult(
            status=LayerStatus.SATISFIED,
            output={
                "task_type": task_type,
                "scope": scope,
                "unknowns": unknowns,
            },
        )

    def check_satisfied(self, context: dict[str, Any]) -> bool:
        return all(
            k in context
            for k in ("task_type", "scope", "unknowns")
        )

    def _classify(self, request: str) -> str:
        """Classify task type from request text."""
        keywords = {
            "bug": ["fix", "bug", "broken", "error", "crash", "fail"],
            "feature": ["add", "create", "new", "implement", "build"],
            "refactor": ["refactor", "clean", "reorganize", "extract", "rename"],
            "question": ["what", "how", "why", "where", "explain", "?"],
            "config": ["config", "setup", "install", "deploy", "env"],
        }
        lower = request.lower()
        scores = {
            task: sum(1 for kw in kws if kw in lower)
            for task, kws in keywords.items()
        }
        return max(scores, key=scores.get) if any(scores.values()) else "unknown"

    def _estimate_scope(self, request: str) -> str:
        """Rough scope estimate: single-file, module, or cross-cutting."""
        lower = request.lower()
        if any(w in lower for w in ["all", "every", "across", "entire", "project"]):
            return "cross-cutting"
        if any(w in lower for w in ["module", "package", "directory", "folder"]):
            return "module"
        return "single-file"

    def _identify_unknowns(self, request: str, context: dict[str, Any]) -> list[str]:
        """List what we don't know yet."""
        unknowns = []
        if "file_tree" not in context:
            unknowns.append("project structure")
        if "target_files" not in context:
            unknowns.append("which files to touch")
        if "test_status" not in context:
            unknowns.append("current test state")
        return unknowns


class Acquire(Layer):
    """
    L2 — ACQUIRE
    Gather raw material: read files, search, grep, fetch.
    Bulk token intake — no interpretation yet.
    """

    index = 2
    name = "acquire"

    def __init__(self):
        self.acquired: list[dict[str, Any]] = []

    def run(self, context: dict[str, Any]) -> LayerResult:
        unknowns = context.get("unknowns", [])
        if not unknowns:
            return LayerResult(status=LayerStatus.SATISFIED)

        acquisition_plan = []
        for unknown in unknowns:
            actions = self._plan_acquisition(unknown)
            acquisition_plan.extend(actions)

        return LayerResult(
            status=LayerStatus.SATISFIED,
            output={
                "acquisition_plan": acquisition_plan,
                "parallel_safe": self._can_parallelize(acquisition_plan),
            },
        )

    def check_satisfied(self, context: dict[str, Any]) -> bool:
        unknowns = context.get("unknowns", [])
        return len(unknowns) == 0

    def _plan_acquisition(self, unknown: str) -> list[dict[str, str]]:
        """Map an unknown to concrete acquisition actions."""
        strategies = {
            "project structure": [
                {"tool": "glob", "args": "**/*", "reason": "map the file tree"},
            ],
            "which files to touch": [
                {"tool": "grep", "args": "<pattern>", "reason": "find relevant files"},
            ],
            "current test state": [
                {"tool": "bash", "args": "test runner", "reason": "check passing/failing"},
            ],
        }
        return strategies.get(unknown, [
            {"tool": "grep", "args": unknown, "reason": f"search for: {unknown}"},
        ])

    def _can_parallelize(self, plan: list[dict]) -> bool:
        """Check if acquisition actions can run in parallel."""
        tools = [a["tool"] for a in plan]
        # reads and greps are safe to parallelize; bash commands may not be
        return all(t in ("glob", "grep", "read") for t in tools)


class Comprehend(Layer):
    """
    L3 — COMPREHEND
    Build a mental model: what does this code do, why.
    Map relationships, trace data flow, identify invariants.
    """

    index = 3
    name = "comprehend"

    def run(self, context: dict[str, Any]) -> LayerResult:
        acquired = context.get("acquired_content", {})
        if not acquired:
            return LayerResult(
                status=LayerStatus.FAILED,
                gaps=["no content acquired yet"],
                fallback_to=2,
            )

        model = {
            "data_flow": self._trace_data_flow(acquired),
            "invariants": self._find_invariants(acquired),
            "conventions": self._detect_conventions(acquired),
            "failure_modes": self._identify_failure_modes(acquired),
        }

        # Only data_flow and invariants are hard requirements.
        # Conventions and failure_modes are nice-to-have.
        required = ("data_flow", "invariants")
        gaps = []
        for key in required:
            if not model.get(key):
                gaps.append(f"could not determine {key}")

        status = LayerStatus.SATISFIED if not gaps else LayerStatus.FAILED
        return LayerResult(
            status=status,
            output={"mental_model": model},
            gaps=gaps,
            fallback_to=2 if gaps else None,
        )

    def check_satisfied(self, context: dict[str, Any]) -> bool:
        model = context.get("mental_model", {})
        return bool(model.get("data_flow")) and bool(model.get("invariants"))

    def _trace_data_flow(self, content: dict[str, str]) -> list[dict]:
        """Trace what calls what across acquired files."""
        # Stub: in practice, parse ASTs or use heuristics
        flows = []
        for filename, source in content.items():
            for i, line in enumerate(source.splitlines()):
                if "import" in line or "require" in line:
                    flows.append({"file": filename, "line": i + 1, "type": "import", "raw": line.strip()})
                if "(" in line and "def " not in line and "class " not in line:
                    flows.append({"file": filename, "line": i + 1, "type": "call", "raw": line.strip()})
        return flows

    def _find_invariants(self, content: dict[str, str]) -> list[str]:
        """Find things that must stay true after changes."""
        invariants = []
        for filename, source in content.items():
            if "assert" in source:
                invariants.append(f"{filename} has assertions that must hold")
            if "raise" in source or "throw" in source:
                invariants.append(f"{filename} has error contracts")
        return invariants

    def _detect_conventions(self, content: dict[str, str]) -> dict[str, str]:
        """Detect naming and style conventions from the code."""
        conventions = {}
        all_source = "\n".join(content.values())
        if "snake_case" in all_source or "_" in all_source:
            conventions["naming"] = "snake_case"
        if "camelCase" in all_source:
            conventions["naming"] = "camelCase"
        if '"""' in all_source:
            conventions["docstrings"] = "google-style"
        return conventions

    def _identify_failure_modes(self, content: dict[str, str]) -> list[str]:
        """Spot what can break."""
        modes = []
        for filename, source in content.items():
            if "try" in source or "except" in source or "catch" in source:
                modes.append(f"{filename} has error handling that may mask issues")
            if "TODO" in source or "FIXME" in source or "HACK" in source:
                modes.append(f"{filename} has known debt markers")
        return modes


class Strategize(Layer):
    """
    L4 — STRATEGIZE
    Sequence the work: what order, what depends on what.
    Build todo lists, dependency graphs, rollback plans.
    """

    index = 4
    name = "strategize"

    def run(self, context: dict[str, Any]) -> LayerResult:
        model = context.get("mental_model", {})
        if not model:
            return LayerResult(
                status=LayerStatus.FAILED,
                gaps=["no mental model built"],
                fallback_to=3,
            )

        task_type = context.get("task_type", "unknown")

        steps = self._sequence_steps(task_type, model)
        risks = self._assess_risk(steps, model)
        verification = self._plan_verification(task_type)
        rollback = self._plan_rollback(steps)

        return LayerResult(
            status=LayerStatus.SATISFIED,
            output={
                "steps": steps,
                "risks": risks,
                "verification": verification,
                "rollback": rollback,
            },
        )

    def check_satisfied(self, context: dict[str, Any]) -> bool:
        return "steps" in context and "verification" in context

    def _sequence_steps(self, task_type: str, model: dict) -> list[dict]:
        """Order the work based on task type and dependencies."""
        # Base ordering varies by task type
        orderings = {
            "bug": ["reproduce", "isolate", "fix", "verify"],
            "feature": ["scaffold", "implement", "integrate", "verify"],
            "refactor": ["identify_pattern", "extract", "replace_usages", "verify"],
            "question": ["gather", "analyze", "respond"],
        }
        phases = orderings.get(task_type, ["analyze", "implement", "verify"])
        return [
            {"phase": phase, "index": i, "depends_on": i - 1 if i > 0 else None}
            for i, phase in enumerate(phases)
        ]

    def _assess_risk(self, steps: list[dict], model: dict) -> list[dict]:
        """Flag risky steps."""
        risks = []
        invariants = model.get("invariants", [])
        if invariants:
            risks.append({
                "concern": "changes may violate invariants",
                "invariants": invariants,
                "mitigation": "run assertions after each edit",
            })
        return risks

    def _plan_verification(self, task_type: str) -> list[str]:
        """How will we know it worked?"""
        base = ["run existing tests"]
        if task_type == "bug":
            base.insert(0, "confirm bug is reproduced first")
            base.append("confirm bug no longer reproduces")
        if task_type == "feature":
            base.append("test new functionality")
        return base

    def _plan_rollback(self, steps: list[dict]) -> list[dict]:
        """For each step, what's the undo?"""
        return [
            {"step": s["phase"], "rollback": f"git revert changes from '{s['phase']}' phase"}
            for s in steps
        ]


class Execute(Layer):
    """
    L5 — EXECUTE
    Produce tokens: edits, responses, tool calls.
    Only entered when all lower layers are satisfied.
    """

    index = 5
    name = "execute"

    def run(self, context: dict[str, Any]) -> LayerResult:
        steps = context.get("steps", [])
        verification = context.get("verification", [])

        if not steps:
            return LayerResult(
                status=LayerStatus.FAILED,
                gaps=["no execution plan"],
                fallback_to=4,
            )

        execution_log = []
        for step in steps:
            result = self._execute_step(step, context)
            execution_log.append(result)
            if result["status"] == "failed":
                return LayerResult(
                    status=LayerStatus.FAILED,
                    output={"execution_log": execution_log},
                    gaps=[f"step '{step['phase']}' failed: {result.get('error', 'unknown')}"],
                    fallback_to=result.get("fallback_to", 3),
                )

        return LayerResult(
            status=LayerStatus.SATISFIED,
            output={
                "execution_log": execution_log,
                "verification_plan": verification,
            },
        )

    def check_satisfied(self, context: dict[str, Any]) -> bool:
        log = context.get("execution_log", [])
        return bool(log) and all(e["status"] == "done" for e in log)

    def _execute_step(self, step: dict, context: dict[str, Any]) -> dict:
        """Execute a single step. Stub — real impl would call tools."""
        return {
            "phase": step["phase"],
            "status": "done",
            "tokens_produced": 0,  # filled by real execution
        }
