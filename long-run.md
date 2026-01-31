# Long Run: Multi-Cycle Path Network

How the 3→6→9 cycle compounds over time. Paths persist, reserves
accumulate, branches fork. Early cycles are scrappy. Late cycles
are infrastructure.

---

## Cycle 1 — Proving Ground

**Turn 1** — Cold start. Three nodes. One path. Must complete to continue.

```
  ○───○
  ○
```

**Turn 2** — First completion. Six nodes unlock.

```
  ○───○───●
  ○───○
  ○
```

**Turn 3** — Saturation. Nine nodes. Two paths completed. Two unused → reserves.

```
  ○───○───●
  ○───○───●───○
  ○───○
  ○
```

```
  completed:  ●●
  reserves:   ○○
```

---

## Cycle 2 — Reset With Memory

**Turn 1** — Back to 3 active nodes. But you kept your paths. And your ammo.

```
  ○───○
  ○

  ╔═══════════╗
  ║ ●───●     ║  ← persistent paths from Cycle 1
  ║ ●───●───● ║
  ╚═══════════╝

  reserves: ○○
```

**Turn 3** — Building. Longer chains. More reserves.

```
  ○───○───●
  ○───○───●───○───●
  ○───○───●
  ○

  ╔═══════════════════╗
  ║ ●───●             ║
  ║ ●───●───●         ║
  ║ ●───●───●───●     ║  ← paths growing
  ╚═══════════════════╝

  reserves: ○○○○
```

---

## Cycle 3 — Momentum

Paths compound. The network thickens.

```
  ╔═══════════════════════════════╗
  ║ ●───●                        ║
  ║ ●───●───●                    ║
  ║ ●───●───●───●                ║
  ║ ●───●───●───●───●            ║
  ║ ●───●───●───●───●───●        ║  ← compounding
  ╚═══════════════════════════════╝

  reserves: ○○○○○○○
```

---

## Cycle 4 — Branching

Paths don't just lengthen. They fork. Options multiply.

```
  ╔═════════════════════════════════════════╗
  ║            ●───●───●                    ║
  ║           ╱                             ║
  ║  ●───●───●                              ║
  ║           ╲                             ║
  ║            ●───●───●───●                ║
  ║                                         ║
  ║  ●───●───●───●───●───●───●              ║
  ╚═════════════════════════════════════════╝

  reserves: ○○○○○○○○○○
```

---

## Cycle 5 — Deep Run

The full network. Branches off branches. Multiple linear chains.
Every new turn has backup. Every path has options.

```
  ╔══════════════════════════════════════════════════════╗
  ║                    ●───●                             ║
  ║                   ╱                                  ║
  ║            ●───●───●───●───●                         ║
  ║           ╱                                          ║
  ║  ●───●───●                                           ║
  ║           ╲                                          ║
  ║            ●───●───●───●                             ║
  ║                     ╲                                ║
  ║                      ●───●───●───●───●               ║
  ║                                                      ║
  ║  ●───●───●───●───●───●───●───●───●                   ║
  ║                                                      ║
  ║  ●───●───●───●───●───●───●                           ║
  ╚══════════════════════════════════════════════════════╝

  reserves: ○○○○○○○○○○○○○○○
```

```
  total bound nodes:    47
  total paths:           7  (3 branched, 4 linear)
  total reserves:       15
  cycles completed:      5
  failures:              0
```

---

## What Failure Looks Like at Cycle 5

One branch dies. The rest survives. Reserves let you rebuild.

```
  ╔══════════════════════════════════════════════════════╗
  ║                    ●───●                             ║
  ║                   ╱                                  ║
  ║            ●───●───✕                                 ║  ← severed
  ║           ╱                                          ║
  ║  ●───●───●                                           ║
  ║           ╲                                          ║
  ║            ●───●───●───●                             ║
  ║                     ╲                                ║
  ║                      ●───●───●───●───●               ║
  ║                                                      ║
  ║  ●───●───●───●───●───●───●───●───●                   ║
  ╚══════════════════════════════════════════════════════╝

  reserves: ○○○○○○○○○○○○○○○  (still intact)
```

The model isn't fragile. It's antifragile.

---

## The Feel

```
  Cycle 1    scrappy, minimal, proving you can complete paths
       ↓
  Cycle 2    paths persist, reserves carry, infrastructure forms
       ↓
  Cycle 3    momentum — chains lengthen, network thickens
       ↓
  Cycle 4    branching — paths fork, options multiply
       ↓
  Cycle 5    deep run — operating from a network, not a prompt
```

Early: you're surviving.
Late: you're governing.

---

## Legend

```
  ○    open node (active / reserve)
  ●    completed node (bound to path)
  ✕    failed node (severed)
  ─    connection between nodes
  ╱ ╲  branch point (path forks)

  ╔══╗
  ║  ║  persistent path network (survives cycle resets)
  ╚══╝
```
