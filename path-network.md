# Path Network: Horizontal Flow

How the 3→6→9 cycle grows a persistent network across cycles.
Turns flow left to right. Cycles continue from where the last ended.
Thickness = hardened path. Branches = earned through emergence.

---

## Reading the Visual

```
───  thin line    first pass, exploratory, fragile, high emergence potential
═══  thick line   hardened, proven, context-rich, safe but no new branches
│    turn break   boundary between turns
║    cycle reset  T3 completed, back to T1 node count but momentum carries
╲    branch       earned via emergence — only appears on thin lines
●    completed    bound node, done
○    open         active or reserve node
◐    dormant      path paused, not dead — retains thickness, not extending
✕    failed       severed node
```

---

## Single Cycle (Cycle 1)

```
T0        │T1             │T2                       │T3                          ┃ reserves
          │               │                         │                           ┃
●───●─────│───●───●───────│───●───●───●─────────────│───●───●───●───●───        ┃
          │   ●───────────│───●───●─────────────────│───●───●───●───            ┃ ○○
          │               │   ●─────────────────────│───●───●───                ┃ ○
          │               │                         │                           ┃
```

---

## Two Cycles

```
T0        │T1             │T2                       │T3                          ║T1              │T2
          │               │                         │                           ║                │
●───●─────│───●───●───────│───●───●───●─────────────│───●───●───●───●───────────║═══●═══●════════│═══●═══●═══●═══
          │   ●───────────│───●───●─────────────────│───●───●───●───────────────║═══●════════════│═══●═══●═══
          │               │   ●─────────────────────│───●───●───────────────────║                │   ●═══
          │               │                         │                           ║                │
```

---

## Three Cycles — Emergence Branch

```
T0        │T1             │T2                       │T3                          ║T1              │T2                       │T3                          ║T1
          │               │                         │                           ║                │                         │                           ║
●───●─────│───●───●───────│───●───●───●─────────────│───●───●───●───●───────────║═══●═══●════════│═══●═══●═══●═════════════│═══●═══●═══●═══●═══════════║═══●═══●═══
          │   ●───────────│───●───●─────────────────│───●───●───●───────────────║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══════════════║═══●═══
          │               │   ●─────────────────────│───●───●───────────────────║                │   ●═════════════════════│═══●═══●═══════════════════║
          │               │                         │                           ║                │                         │           ╲               ║
          │               │                         │                           ║                │                         │            ●───●───●──    ║
          │               │                         │                           ║                │                         │                           ║
```

The `╲` at C3:T3 — emergence earned a branch. That branch starts thin.

---

## Five Cycles — Full Network

```
C1                                                                               C2                                                                              C3
T0        │T1             │T2                       │T3                          ║T1              │T2                       │T3                          ║T1              │T2                       │T3
          │               │                         │                           ║                │                         │                           ║                │                         │
●───●─────│───●───●───────│───●───●───●─────────────│───●───●───●───●───────────║═══●═══●════════│═══●═══●═══●═════════════│═══●═══●═══●═══●═══════════║═══●═══●════════│═══●═══●═══●═════════════│═══●═══●═══●═══●═══
          │   ●───────────│───●───●─────────────────│───●───●───●───────────────║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══════════════║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══
          │               │   ●─────────────────────│───●───●───────────────────║                │   ●═════════════════════│═══●═══●═══════════════════║                │   ●═════════════════════│═══●═══●═══
          │               │                         │                           ║                │                         │           ╲               ║                │                         │
          │               │                         │                           ║                │                         │            ●───●───●──────║═══●════════════│═══●═══●═══════════════  │
          │               │                         │                           ║                │                         │                           ║                │          ╲              │
          │               │                         │                           ║                │                         │                           ║                │           ●───●───      │


          C4                                                                              C5
          ║T1              │T2                       │T3                          ║T1              │T2                       │T3
          ║                │                         │                           ║                │                         │
──────────║═══●═══●════════│═══●═══●═══●═════════════│═══●═══●═══●═══●═══════════║═══●═══●════════│═══●═══●═══●═════════════│═══●═══●═══●═══●
──────────║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══════════════║═══●════════════│═══●═══●═════════════════│═══●═══●═══●
──────────║                │   ●═════════════════════│═══●═══●═══════════════════║                │   ●═════════════════════│═══●═══●
          ║                │                         │                           ║                │                         │
──────────║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══════════════║═══●════════════│═══●═══●═════════════════│═══●═══●═══●
          ║                │                         │          ╲                ║                │                         │
          ║                │                         │           ●───●───●───────║═══●════════════│═══●═══●═══              │
──────────║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══════════════║═══●════════════│═══●═══●═════════════════│═══●═══●═══●═══●
          ║                │                         │                           ║                │                         │
```

---

## Failure at Depth

```
═══●═══●═══●═══●═══●═══════════════│═══●═══●═══●═══●═══════════════║═══●═══●     ┃ reserves
═══●═══●═══●═══════════════════════│═══●═══●═══●═══════════════════║═══●════     ┃ ○○○○○
                   ╲               │                                ║             ┃ ○○○
                    ●───●───✕      │                                ║             ┃
                                   │                                ║             ┃ ○
═══●═══●═══●═══●═══════════════════│═══●═══●═══●═══●═══════════════║═══●═══●     ┃
═══●═══●═══════════════════════════│═══●═══●═══●═══════════════════║═══●════     ┃
```

The `✕` kills one thin branch. Every thick line survives.
Reserves are still intact — rebuild material is visible in the gutter.

---

## Dormant Paths

Some paths aren't failed, just sleeping. They retain their thickness
and context but aren't actively extending. This matters for long-running
projects that get backgrounded.

```
═══●═══●═══●═══●═══●═══════════════│═══●═══●═══●═══●═══════════════║═══●═══●     active
═══●═══●═══●═══◐                                                                  dormant — paused, not dead
                   ╲               │                                ║
                    ●───●───●──────│───●───●───●───●────────────────║═══●═══●     active (branched)
                                   │                                ║
═══●═══●═══●═══●═══◐                                                              dormant — backgrounded
```

`◐` marks where a path went dormant. The thick line behind it is preserved.
When the project resurfaces, the path can resume from `◐` without
rebuilding — the context is still there.

---

## What Thickness Means

```
thin ───    exploratory, first pass
            fragile — failure severs
            high emergence potential — ╲ branches spawn here
            less context carried

                    │
                    ▼  (consistency proven, KPIs met)

thick ═══   hardened, proven trajectory
            resilient — failure absorbed
            no new branches — discovery phase over
            rich context, safety net for the network
```

Thick lines are infrastructure.
Thin lines are R&D.
A healthy network has both.

---

## Node States at a Glance

```
●    alive, completed         path is proven
○    open, reserve            ammo in the gutter — available for rebuild or extension
◐    dormant                  paused, retains thickness, resumable
✕    failed                   severed, branch is dead
╲    branch point             earned through emergence — only on thin lines
```
