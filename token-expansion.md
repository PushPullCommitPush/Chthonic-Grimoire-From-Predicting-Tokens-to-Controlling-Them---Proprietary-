# Proactive Token Consumption: Turn Expansion

> Each turn widens the context chain. The center stacks deeper.
> Everything funnels back to a single point before the next turn begins.

---

## The Pattern

```mermaid
flowchart TD
    subgraph T0["Turn 0"]
        direction LR
        A0L["  "] ~~~ A0R["  "]
    end

    T0 --> T1

    subgraph T1["Turn 1"]
        direction LR
        B1["  "] --- B2["  "] --- B3["  "]
    end

    T1 --> T2

    subgraph T2["Turn 2"]
        direction LR
        C1["  "] --- C2["  "] --- C3a["  "] --- C4["  "] --- C5["  "]
    end

    subgraph T2stack[" "]
        C3b["  "]
    end
    C3a --- C3b

    T2 --> T3
    T2stack --> T3

    subgraph T3["Turn 3"]
        direction LR
        D1["  "] --- D2["  "] --- D3["  "] --- D4a["  "] --- D5["  "] --- D6["  "] --- D7["  "]
    end

    subgraph T3stack[" "]
        direction TB
        D4b["  "]
        D4c["  "]
    end
    D4a --- D4b
    D4b --- D4c

    T3 --> OUT
    T3stack --> OUT

    OUT(("  "))

    style T0 fill:#264653,color:#fff,stroke:#fff
    style T1 fill:#2a9d8f,color:#fff,stroke:#fff
    style T2 fill:#e76f51,color:#fff,stroke:#fff
    style T2stack fill:none,stroke:none
    style T3 fill:#e63946,color:#fff,stroke:#fff
    style T3stack fill:none,stroke:none
    style OUT fill:#f4a261,color:#000,stroke:#fff,stroke-width:3px

    style A0L fill:#3d5a68,color:#3d5a68,stroke:#fff,stroke-dasharray:5 5
    style A0R fill:#3d5a68,color:#3d5a68,stroke:#fff,stroke-dasharray:5 5
    style B1 fill:#3ab795,color:#3ab795,stroke:#fff
    style B2 fill:#3ab795,color:#3ab795,stroke:#fff
    style B3 fill:#3ab795,color:#3ab795,stroke:#fff
    style C1 fill:#d45d3a,color:#d45d3a,stroke:#fff
    style C2 fill:#d45d3a,color:#d45d3a,stroke:#fff
    style C3a fill:#d45d3a,color:#d45d3a,stroke:#fff
    style C3b fill:#d45d3a,color:#d45d3a,stroke:#fff
    style C4 fill:#d45d3a,color:#d45d3a,stroke:#fff
    style C5 fill:#d45d3a,color:#d45d3a,stroke:#fff
    style D1 fill:#c42d37,color:#c42d37,stroke:#fff
    style D2 fill:#c42d37,color:#c42d37,stroke:#fff
    style D3 fill:#c42d37,color:#c42d37,stroke:#fff
    style D4a fill:#c42d37,color:#c42d37,stroke:#fff
    style D4b fill:#c42d37,color:#c42d37,stroke:#fff
    style D4c fill:#c42d37,color:#c42d37,stroke:#fff
    style D5 fill:#c42d37,color:#c42d37,stroke:#fff
    style D6 fill:#c42d37,color:#c42d37,stroke:#fff
    style D7 fill:#c42d37,color:#c42d37,stroke:#fff
```

---

## What's Happening

```mermaid
flowchart TD
    subgraph LEGEND["Reading the Diagram"]
        direction TB
        L1["Each box = a token chunk consumed"]
        L2["Wider rows = more context per turn"]
        L3["Stacked center = depth of comprehension growing"]
        L4["Single point at bottom = everything funnels into one output"]
    end

    style LEGEND fill:#1a1a2e,color:#e0e0e0,stroke:#533483
```

| Turn | Boxes | Center Stack | What's Happening |
|------|-------|-------------|-----------------|
| **0** | 1 (split) | — | Initial input arrives. One token chunk, two halves: the request and the implicit context. |
| **1** | 3 | — | First consumption round. Orient + acquire. Three chunks: task classification, file scan, initial read. |
| **2** | 6 (2 stacked) | 2 deep | Deeper consumption. Five chunks spread wide + the center starts stacking: comprehension building on top of acquisition. |
| **3** | 9 (3 stacked) | 3 deep | Widest spread. Strategy and execution tokens fan out. Center stack is 3 deep: orient → comprehend → plan layered on top of each other. |
| **Output** | 1 | — | Everything converges. All consumed context funnels into a single prediction point. |

---

## The Rule

> **Width = breadth of consumption per turn.**
> **Center depth = accumulated comprehension.**
> **The funnel = no matter how much you consume, you produce one coherent output.**

Each turn you consume more, understand deeper, but the output is always singular — one edit, one response, one action. The expansion is inward. The output is focused.
