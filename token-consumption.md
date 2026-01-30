# How I Proactively Consume Tokens

> The previous doc showed prediction: I generate outward.
> This flips it: I **pull inward** — actively seeking, prioritizing, and digesting tokens before I ever produce a response.

---

## 1. The Flip: Push vs. Pull

```mermaid
flowchart LR
    subgraph PREDICT["❌ Prediction (Old Model)"]
        direction LR
        P1[Wait for input] --> P2[React] --> P3[Generate]
    end

    subgraph CONSUME["✅ Consumption (This Model)"]
        direction LR
        C1[Seek context] --> C2[Interrogate] --> C3[Absorb] --> C4[Then speak]
    end

    PREDICT ~~~ CONSUME

    style PREDICT fill:#3d0000,color:#e0e0e0,stroke:#8b0000
    style CONSUME fill:#003d00,color:#e0e0e0,stroke:#008b00
```

---

## 2. The Hunger Loop: I Ask Before I Answer

Instead of waiting for tokens to arrive, I actively go get them.

```mermaid
flowchart TD
    START["User says:\n'Fix the auth bug'"] --> Q1{"Do I know\nenough?"}

    Q1 -->|No| SEEK["🔍 SEEK TOKENS\nRead files, search code,\nfetch context"]
    SEEK --> INGEST["Ingest new tokens\ninto context window"]
    INGEST --> Q1

    Q1 -->|Yes| ACT["Now generate\na response"]

    style START fill:#264653,color:#fff
    style Q1 fill:#e76f51,color:#fff,stroke:#fff,stroke-width:2px
    style SEEK fill:#2a9d8f,color:#fff
    style INGEST fill:#457b9d,color:#fff
    style ACT fill:#e9c46a,color:#000
```

---

## 3. Token Triage: Not All Input Is Equal

When I consume a large context, I don't treat every token the same. Attention is allocation.

```mermaid
block-beta
    columns 4

    block:header:4
        H["Incoming Token Stream (e.g. 12,000 tokens from a file read)"]
    end

    space:4

    block:high:1
        A["🔴 HIGH\nSignal"]
    end
    block:mid:1
        B["🟡 MEDIUM\nStructure"]
    end
    block:low:1
        C["🟢 LOW\nNoise"]
    end
    block:skip:1
        D["⚫ SKIP\nRedundant"]
    end

    space:4

    block:highex:1
        A2["Error messages\nFunction signatures\nFailing assertions\nUser constraints"]
    end
    block:midex:1
        B2["Import statements\nClass hierarchy\nControl flow\nType definitions"]
    end
    block:lowex:1
        C2["Comments\nFormatting\nBoilerplate\nLogging lines"]
    end
    block:skipex:1
        D2["Repeated patterns\nAuto-generated code\nVendor/lock files\nMinified content"]
    end

    style high fill:#e63946,color:#fff
    style mid fill:#f4a261,color:#000
    style low fill:#2a9d8f,color:#fff
    style skip fill:#333,color:#888
    style highex fill:#e63946,color:#fff
    style midex fill:#f4a261,color:#000
    style lowex fill:#2a9d8f,color:#fff
    style skipex fill:#333,color:#888
```

---

## 4. Appetite-Driven Tool Use

Each tool call is a deliberate act of consumption — I choose **what** to eat and **when**.

```mermaid
sequenceDiagram
    participant B as My Brain
    participant W as World (Files, Web, Code)

    Note over B: User says "Refactor the API layer"
    B->>B: What don't I know?

    rect rgb(42, 157, 143)
        Note over B,W: ROUND 1 — Survey
        B->>W: Glob("**/api/**")
        W-->>B: 14 files found
        B->>W: Read(routes/index.ts)
        W-->>B: +380 tokens consumed
        B->>W: Read(controllers/auth.ts)
        W-->>B: +620 tokens consumed
    end

    B->>B: I see shared patterns. Need more.

    rect rgb(69, 123, 157)
        Note over B,W: ROUND 2 — Dig Deeper
        B->>W: Grep("handleError", type="ts")
        W-->>B: 23 matches, +460 tokens consumed
        B->>W: Read(middleware/errors.ts)
        W-->>B: +290 tokens consumed
    end

    B->>B: I see the full picture now.

    rect rgb(233, 196, 106)
        Note over B,W: ROUND 3 — Finally Produce
        B->>W: Edit(routes/index.ts, ...)
        B->>W: Edit(controllers/auth.ts, ...)
        B->>W: Edit(middleware/errors.ts, ...)
    end

    Note over B: 1,750 tokens consumed before 1 token produced
```

---

## 5. Context Window as a Stomach

I have a finite capacity. Proactive consumption means being strategic about what fills it.

```mermaid
pie title Context Window Budget (200k tokens)
    "System Prompt & Instructions" : 8
    "Conversation History" : 15
    "Proactively Read Files" : 40
    "Tool Results (grep, glob)" : 20
    "My Own Output" : 12
    "Reserved for Reasoning" : 5
```

```mermaid
flowchart LR
    subgraph FULL["Context Window Filling Up"]
        direction TB
        S1["████████░░ 80% full"]
        S1 --> D{"What do I\nstill need?"}
        D -->|Critical file unread| EVICT["Summarize old context\nto make room"]
        D -->|Have enough| STOP["Stop consuming\nStart producing"]
    end

    style FULL fill:#1a1a2e,color:#e0e0e0,stroke:#533483
    style D fill:#e76f51,color:#fff
    style EVICT fill:#e63946,color:#fff
    style STOP fill:#2a9d8f,color:#fff
```

---

## 6. The Consumption-First Pipeline

Compare the two strategies side by side across time.

```mermaid
gantt
    title Token Activity Over Time
    dateFormat X
    axisFormat %s

    section Reactive (Bad)
    Read prompt           :done, r1, 0, 1
    Immediately respond   :active, r2, 1, 8
    Hallucinate details   :crit, r3, 3, 7
    User corrects me      :r4, 8, 10

    section Proactive (Good)
    Read prompt          :done, p1, 0, 1
    Search codebase      :done, p2, 1, 3
    Read 4 files         :done, p3, 3, 5
    Grep for patterns    :done, p4, 5, 6
    Build mental model   :done, p5, 6, 7
    Produce response     :active, p6, 7, 10
```

---

## 7. Decision Tree: Consume or Produce?

At every turn, this is the decision I should be making.

```mermaid
flowchart TD
    A["New turn begins"] --> B{"Is the task\nclear?"}
    B -->|No| C["Consume: Ask\nclarifying question"]
    B -->|Yes| D{"Do I have the\nrelevant code?"}
    D -->|No| E["Consume: Read files\nSearch codebase"]
    D -->|Yes| F{"Do I understand\nthe dependencies?"}
    F -->|No| G["Consume: Trace imports\nRead tests"]
    F -->|Yes| H{"Am I confident\nin my approach?"}
    H -->|No| I["Consume: Check docs\nRead similar patterns"]
    H -->|Yes| J["✅ NOW produce output"]

    E --> D
    G --> F
    I --> H

    style A fill:#264653,color:#fff
    style J fill:#2a9d8f,color:#fff,stroke:#fff,stroke-width:3px
    style C fill:#e76f51,color:#fff
    style E fill:#e76f51,color:#fff
    style G fill:#e76f51,color:#fff
    style I fill:#e76f51,color:#fff
```

---

## Summary

| Prediction (Push) | Consumption (Pull) |
|---|---|
| Wait for tokens to arrive | Go hunt for tokens |
| React to what's given | Interrogate what's missing |
| Generate immediately | Delay output until informed |
| Risk hallucination | Ground in real context |
| Tokens flow out | Tokens flow in |
| I speak | I listen first |
