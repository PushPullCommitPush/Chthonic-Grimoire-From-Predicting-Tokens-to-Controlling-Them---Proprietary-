# How I Predict & Plan Token Inputs and Outputs

## 1. The Big Picture

```mermaid
flowchart LR
    subgraph INPUT["📥 Input Phase"]
        A[User Prompt] --> B[Tokenizer]
        B --> C[Token IDs]
        C --> D[Embeddings]
    end

    subgraph PROCESS["⚙️ Processing Phase"]
        D --> E[Self-Attention\nLayers x N]
        E --> F[Probability\nDistribution]
    end

    subgraph OUTPUT["📤 Output Phase"]
        F --> G{Sample\nNext Token}
        G --> H[Output Token]
        H -->|Feed back as input| E
        H --> I[Detokenize]
        I --> J[Response Text]
    end

    style INPUT fill:#1a1a2e,color:#e0e0e0,stroke:#16213e
    style PROCESS fill:#16213e,color:#e0e0e0,stroke:#0f3460
    style OUTPUT fill:#0f3460,color:#e0e0e0,stroke:#533483
```

## 2. Tokenization: Text → Numbers

Raw text is split into subword tokens before I ever see it.

```mermaid
block-beta
    columns 7
    block:input:7
        A["Input: 'How does tokenization work?'"]
    end
    space:7
    T1["How"] T2[" does"] T3[" token"] T4["ization"] T5[" work"] T6["?"] space
    space:7
    I1["8090"] I2["1464"] I3["4037"] I4["2065"] I5["990"] I6["30"] space

    style T1 fill:#e63946,color:#fff
    style T2 fill:#457b9d,color:#fff
    style T3 fill:#2a9d8f,color:#fff
    style T4 fill:#e9c46a,color:#000
    style T5 fill:#f4a261,color:#000
    style T6 fill:#264653,color:#fff
    style I1 fill:#e63946,color:#fff
    style I2 fill:#457b9d,color:#fff
    style I3 fill:#2a9d8f,color:#fff
    style I4 fill:#e9c46a,color:#000
    style I5 fill:#f4a261,color:#000
    style I6 fill:#264653,color:#fff
```

## 3. Self-Attention: How I Decide What Matters

Each token attends to every other token. Stronger connections = more influence.

```mermaid
flowchart TD
    subgraph ATTENTION["Attention Weights (simplified)"]
        direction LR
        W1["The"] ---|0.1| W2["cat"]
        W2 ---|0.8| W3["sat"]
        W1 ---|0.3| W3
        W3 ---|0.9| W4["on"]
        W4 ---|0.7| W5["the"]
        W5 ---|0.9| W6["___"]
        W2 ---|0.6| W6
        W3 ---|0.4| W6
        W4 ---|0.5| W6
    end

    W6 --> PRED["Prediction: 'mat' (0.35) | 'floor' (0.20) | 'rug' (0.12) | ..."]

    style W2 fill:#e63946,color:#fff
    style W3 fill:#457b9d,color:#fff
    style W6 fill:#2a9d8f,color:#fff,stroke:#fff,stroke-width:3px
    style PRED fill:#264653,color:#fff
```

## 4. Autoregressive Generation: One Token at a Time

I generate output **sequentially** — each new token becomes input for the next.

```mermaid
sequenceDiagram
    participant U as User Prompt
    participant M as Model
    participant O as Output Buffer

    U->>M: "What is 2+2?"
    M->>M: Process all input tokens
    M->>O: "The" (p=0.42)
    Note over M: Input is now: "What is 2+2? The"
    M->>O: " answer" (p=0.71)
    Note over M: Input is now: "...? The answer"
    M->>O: " is" (p=0.89)
    Note over M: Input is now: "...The answer is"
    M->>O: " 4" (p=0.95)
    Note over M: Input is now: "...answer is 4"
    M->>O: "." (p=0.78)
    M->>O: "[STOP]"
    O->>U: "The answer is 4."
```

## 5. Planning Across a Multi-Turn Task

When handling tool use and multi-step tasks, the full context accumulates.

```mermaid
flowchart TD
    subgraph TURN1["Turn 1: User Request"]
        R1["User: 'Fix the bug in auth.py'"]
        R1 --> P1["Plan: I need to\n1. Read the file\n2. Identify the bug\n3. Fix it"]
    end

    subgraph TURN2["Turn 2: Tool Call"]
        P1 --> T1["Generate tokens:\n'Read(auth.py)'"]
        T1 --> TR["Tool returns\nfile contents"]
    end

    subgraph TURN3["Turn 3: Analysis"]
        TR --> A1["All prior tokens +\nfile contents = new input"]
        A1 --> A2["Identify bug at line 42:\nmissing null check"]
    end

    subgraph TURN4["Turn 4: Fix"]
        A2 --> F1["Generate edit tokens\ntargeting line 42"]
        F1 --> F2["Output: Edit tool call\nwith fix applied"]
    end

    style TURN1 fill:#1a1a2e,color:#e0e0e0,stroke:#533483
    style TURN2 fill:#16213e,color:#e0e0e0,stroke:#533483
    style TURN3 fill:#0f3460,color:#e0e0e0,stroke:#533483
    style TURN4 fill:#533483,color:#e0e0e0,stroke:#e94560
```

## 6. The Token Probability Cascade

At each step, I see a probability distribution over ~100k possible next tokens.

```mermaid
xychart-beta
    title "Next-Token Probabilities for: 'The capital of France is ___'"
    x-axis ["Paris", "the", "located", "a", "known", "Lyon", "called", "in", "not", "..."]
    y-axis "Probability" 0 --> 1
    bar [0.92, 0.02, 0.015, 0.008, 0.007, 0.005, 0.004, 0.003, 0.002, 0.016]
```

## Key Takeaways

| Concept | How It Works |
|---|---|
| **Tokenization** | Text is split into subword chunks, each mapped to an integer ID |
| **Embedding** | Token IDs become high-dimensional vectors carrying semantic meaning |
| **Self-Attention** | Every token "looks at" every other token to build contextual understanding |
| **Autoregressive** | Output is generated one token at a time; each feeds back as input |
| **Planning** | Multi-step reasoning emerges from accumulated context across turns |
| **Sampling** | The next token is selected from a probability distribution over the vocabulary |
