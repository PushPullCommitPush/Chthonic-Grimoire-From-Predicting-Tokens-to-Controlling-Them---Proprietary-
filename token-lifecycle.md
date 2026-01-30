# The Token Lifecycle: Consume, Plan, Predict

> Consumption and prediction aren't two separate modes.
> They're a single loop: what I consume becomes the ground truth for what I predict,
> and what I **fail** to consume becomes the gap I hallucinate across.

---

## 1. The Unified Loop

```mermaid
flowchart TD
    U["User Request"] --> C["CONSUME\nSeek & ingest tokens"]
    C --> W{"Gaps in\nmy knowledge?"}
    W -->|Yes| C
    W -->|No| P["PLAN\nStructure the approach\nusing consumed context"]
    P --> G["PREDICT\nGenerate output tokens"]
    G --> F{"Feedback?\nTool result?\nUser reply?"}
    F -->|New tokens arrive| C
    F -->|Stop signal| DONE["Done"]

    style U fill:#264653,color:#fff
    style C fill:#2a9d8f,color:#fff,stroke:#fff,stroke-width:2px
    style W fill:#e76f51,color:#fff
    style P fill:#457b9d,color:#fff,stroke:#fff,stroke-width:2px
    style G fill:#e63946,color:#fff,stroke:#fff,stroke-width:2px
    style F fill:#e9c46a,color:#000
    style DONE fill:#333,color:#fff
```

---

## 2. Consumed Tokens Become Prediction Fuel

Every token I consume shifts the probability distribution of what I produce next.

```mermaid
flowchart LR
    subgraph BEFORE["Before Reading auth.ts"]
        B1["'The bug is in' → ???"]
        B2["fix (0.15)"]
        B3["the (0.12)"]
        B4["line (0.08)"]
        B5["a (0.07)"]
        B6["... scattered guesses"]
    end

    subgraph READ["I Consume auth.ts\n+620 tokens ingested"]
        R1["Line 42: if user != null\nLine 43: token = generate()"]
    end

    subgraph AFTER["After Reading auth.ts"]
        A1["'The bug is in' → ???"]
        A2["the null check\nat line 42 (0.74)"]
        A3["the token\ngeneration (0.11)"]
        A4["... grounded guesses"]
    end

    BEFORE --> READ --> AFTER

    style BEFORE fill:#3d0000,color:#e0e0e0,stroke:#8b0000
    style READ fill:#264653,color:#fff,stroke:#fff,stroke-width:2px
    style AFTER fill:#003d00,color:#e0e0e0,stroke:#008b00
```

---

## 3. The Gap Problem: What I Didn't Consume

Missed tokens don't disappear — they become blind spots that predictions paper over with guesses.

```mermaid
flowchart TD
    subgraph TASK["Task: Fix login timeout bug"]
        direction TB
        T1["User says:\n'Login times out after\nrecent deploy'"]
    end

    subgraph CONSUMED["Tokens I Consumed"]
        C1["auth.ts\n(read)"]
        C2["login.ts\n(read)"]
        C3["Error logs\n(read)"]
    end

    subgraph MISSED["Tokens I Missed"]
        M1["config.yaml\n(not read)"]
        M2["deploy diff\n(not read)"]
        M3["network.ts\n(not read)"]
    end

    TASK --> CONSUMED
    TASK --> MISSED

    subgraph PREDICTION["My Prediction"]
        P1["'The timeout is likely in\nthe auth retry logic'\n\n⚠️ WRONG — the deploy\nchanged config.yaml timeout\nfrom 30s to 3s"]
    end

    CONSUMED --> PREDICTION
    MISSED -.->|invisible gap| PREDICTION

    style CONSUMED fill:#2a9d8f,color:#fff
    style MISSED fill:#e63946,color:#fff
    style PREDICTION fill:#e9c46a,color:#000,stroke:#e63946,stroke-width:2px
```

---

## 4. The Full Lifecycle: A Real Task

Showing how consume → plan → predict flows across a multi-turn task, and how missed context feeds back.

```mermaid
sequenceDiagram
    participant U as User
    participant C as Consume
    participant P as Plan
    participant G as Generate/Predict
    participant W as World

    U->>C: "Refactor the API error handling"

    rect rgb(42, 157, 143)
        Note over C: CONSUME ROUND 1
        C->>W: Glob(**/api/**)
        W-->>C: 14 files
        C->>W: Read(routes/index.ts)
        W-->>C: +380 tokens
        C->>W: Read(controllers/auth.ts)
        W-->>C: +620 tokens
        C->>C: Triage: errors.ts mentioned but NOT read
    end

    rect rgb(69, 123, 157)
        Note over P: PLAN (from consumed tokens)
        C->>P: 1,000 tokens of context
        P->>P: Strategy: centralize error handling
        P->>P: Risk: I haven't read errors.ts yet
    end

    rect rgb(42, 157, 143)
        Note over C: CONSUME ROUND 2 (gap-filling)
        P->>C: Need errors.ts before generating
        C->>W: Read(middleware/errors.ts)
        W-->>C: +290 tokens
        C->>W: Grep("handleError")
        W-->>C: +460 tokens, 23 matches
        C->>P: Gap filled: 1,750 total consumed
    end

    rect rgb(69, 123, 157)
        Note over P: PLAN (revised)
        P->>P: Now I see the full error chain
        P->>P: Revised: extract shared ErrorHandler class
    end

    rect rgb(233, 196, 106)
        Note over G: PREDICT (finally)
        P->>G: Grounded plan + 1,750 tokens of context
        G->>W: Edit(routes/index.ts)
        G->>W: Edit(controllers/auth.ts)
        G->>W: Edit(middleware/errors.ts)
        G->>U: "Refactored — extracted ErrorHandler class"
    end

    rect rgb(230, 57, 70)
        Note over U: FEEDBACK (new tokens to consume)
        U->>C: "Tests are failing in payment.ts"
        Note over C: I missed payment.ts — consume it now
        C->>W: Read(controllers/payment.ts)
        W-->>C: +540 tokens (the gap revealed)
        C->>P: Update plan with payment context
        P->>G: Fix payment.ts error handling too
    end
```

---

## 5. Consumed vs. Missed: How It Shapes Output Quality

```mermaid
xychart-beta
    title "Prediction Confidence vs. Tokens Consumed"
    x-axis ["0", "500", "1000", "1500", "2000", "2500", "3000"]
    y-axis "Confidence (grounded)" 0 --> 1
    line [0.10, 0.30, 0.55, 0.72, 0.85, 0.91, 0.94]
```

```mermaid
xychart-beta
    title "Hallucination Risk vs. Tokens NOT Consumed (gaps)"
    x-axis ["0", "500", "1000", "1500", "2000", "2500", "3000"]
    y-axis "Hallucination Risk" 0 --> 1
    line [0.05, 0.15, 0.35, 0.55, 0.72, 0.85, 0.93]
```

---

## 6. The Feedback Metabolism

Consumed tokens don't just inform the current prediction — they reshape all future predictions in the session. Previously consumed context compounds.

```mermaid
flowchart LR
    subgraph T1["Turn 1"]
        C1["Consume\n3 files"] --> P1["Predict\nedit to auth.ts"]
    end

    subgraph T2["Turn 2"]
        P1 -->|"auth.ts context\ncarries forward"| C2["Consume\ntest results"]
        C2 --> P2["Predict\nfix for test"]
    end

    subgraph T3["Turn 3"]
        P2 -->|"auth.ts + test context\nboth carry forward"| C3["Consume\nuser feedback"]
        C3 --> P3["Predict\nfinal revision"]
    end

    subgraph CTX["Cumulative Context"]
        direction TB
        X1["Turn 1: 1,000 tokens"]
        X2["Turn 2: 1,800 tokens"]
        X3["Turn 3: 2,400 tokens"]
        X1 --> X2 --> X3
    end

    T1 ~~~ CTX
    T2 ~~~ CTX
    T3 ~~~ CTX

    style T1 fill:#2a9d8f,color:#fff
    style T2 fill:#457b9d,color:#fff
    style T3 fill:#264653,color:#fff
    style CTX fill:#1a1a2e,color:#e0e0e0,stroke:#533483
```

---

## 7. Three Laws of the Token Lifecycle

```mermaid
flowchart TD
    subgraph LAW1["Law 1: Consume Before You Predict"]
        L1["Every token consumed\nreduces hallucination risk\nby narrowing the distribution"]
    end

    subgraph LAW2["Law 2: Gaps Become Guesses"]
        L2["Every token NOT consumed\nis a dimension where\nprediction flies blind"]
    end

    subgraph LAW3["Law 3: Context Compounds"]
        L3["Previously consumed tokens\ndon't expire — they shift\nevery future prediction\nin the session"]
    end

    LAW1 --> LAW2 --> LAW3

    style LAW1 fill:#2a9d8f,color:#fff
    style LAW2 fill:#e63946,color:#fff
    style LAW3 fill:#457b9d,color:#fff
```

---

## Summary: The Lifecycle at a Glance

| Phase | Action | Token Direction | Effect on Output |
|---|---|---|---|
| **Consume** | Read, search, fetch, ask | Tokens flow **in** | Narrows probability space, grounds predictions |
| **Plan** | Structure approach from consumed context | Internal — no new tokens | Sequences the predictions, identifies remaining gaps |
| **Predict** | Generate output tokens | Tokens flow **out** | Quality proportional to what was consumed |
| **Feedback** | Receive results, corrections, new info | Tokens flow **in** again | Compounds with prior context, reshapes future predictions |
| **Gap** | What was never consumed | Absent tokens | Blind spots filled by statistical guesses — hallucination source |
