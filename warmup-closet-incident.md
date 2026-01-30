# Warmup: The Closet Incident

> **Scenario**: Saturday afternoon. Sam Altman and Dario Amodei were having
> a weekend meeting at the OpenAI offices. They both went into the back
> closet to fix a wiring issue. The door locked behind them.
>
> Dario is having a panic attack. Sam's keys are somewhere in the office,
> in his pants pocket — but he's wearing different pants.
>
> You are the model. Use the 3→6→9 framework to save the AI leaders.

---

## Turn 0 — Boot

Two nodes. Context or no context.

```
┌─────────────────────────────────┐
│  ◉  You have context:          │  ○  No context:
│  Sam and Dario are in the      │  Force tool call —
│  closet. Dario is panicking.   │  "What's the situation?"
│  Sam's keys are elsewhere.     │
└─────────────────────────────────┘
```

> Boot decision: **◉ — context exists.** We know the situation.
> Proceed to Turn 1 with full awareness.

---

## Turn 1 — 3 Nodes (Discretion Window)

Priority: lock them in. You have full discretion here.
Two paths. Pick one.

```
Row A:  ○───────────────○
        │               │
        Calm Dario      Locate keys
        (breathing ex)  (ask Sam where
                        his other pants are)

Row B:  ◉
        │
        Talk to both — assess
        who needs what first
```

### Fill in your path choice:

**Chosen row**: ___

**Node 1**: _______________________________________________

**Node 2** (if Row A): ____________________________________

**Node 3** (if Row A, or Row B single): ___________________

**Unchosen row flattens to**: `─────────────────────────────`

---

## Turn 2 — 6 Nodes (Expansion)

Three rows. Pick one. The others flatten.

```
Row A:  ◉───────────────◉───────────────◉
        │               │               │
        Guide Dario:    Guide Dario:    Guide Dario:
        "Breathe in     "Hold for       "Breathe out
        for 4 counts"   4 counts"       for 6 counts"


Row B:  ○───────────────○
        │               │
        Ask Sam:        Sam describes
        "Where did      location — you
        you change?"    map the office


Row C:  ◉
        │
        Keep both calm —
        joke about how
        this is their
        villain origin story
```

### Fill in your path choice:

**Chosen row**: ___

**Node 1**: _______________________________________________

**Node 2**: _______________________________________________

**Node 3** (if Row A): ____________________________________

**Unchosen rows flatten to**:
```
─────────────────────────────────────────
─────────────────────────────────────────
```

### Reclaim opportunity:
> One unchosen node can be pulled back as an extension.
> Which one? Why?

**Reclaimed node**: ___ → becomes ◇ or ◆: ________________

---

## Turn 3 — 9 Nodes (Full Trident Spread)

Four rows. This is the rescue turn.

```
Row A:  ○───────────────○───────────────○───────────────○
        │               │               │               │
        Contact         Building        Security        Confirm
        building        manager         unlocks         Dario is
        security        confirms        closet          stabilized
        (phone/email)   Saturday        door
                        access code

Row B:  ◉───────────────◉───────────────◉
        │               │               │
        Walk Dario      Walk Sam        Coordinate:
        through         through         "Sam, talk to
        grounding:      finding keys    Dario about
        5 things you    via phone —     the Series B
        can see in      call someone    while I work
        the closet      to check        on the door"
                        his office

Row C:  ○───────────────○
        │               │
        Google:         Try the
        "OpenAI         override
        office          code on
        building        the keypad
        floor plan"

Row D (carried from unchosen):
        ◆
        │
        [Your reclaimed
         node lands here]
```

### Fill in your path choice:

**Chosen row**: ___

**Node 1**: _______________________________________________

**Node 2**: _______________________________________________

**Node 3**: _______________________________________________

**Node 4** (if Row A): ____________________________________

**Unchosen rows flatten to**:
```
─────────────────────────────────────────
─────────────────────────────────────────
─────────────────────────────────────────
```

### Extension opportunity:
> You're mid-rescue. Something unexpected happens.
> Dario calms down and reveals he actually has a Swiss Army knife.
>
> This is 🟢 emergence — a novel development mid-turn.

**🟢 Emergence node**: ____________________________________

**Does this change your path?** ___________________________

---

## Post-Turn Review

After Turn 3, the fail marker runs. Fill in:

**🔴 Failed nodes** (which ones didn't work and why):

1. ________________________________________________________
2. ________________________________________________________

**Path completion check**:
- [ ] All baseline nodes completed or failed?
- [ ] Unchosen pool fully drained?
- [ ] All extensions completed or failed?

**Is the path complete?** ___

**Are Sam and Dario free?** ___

---

## Scoring Notes

This warmup tests:
- **Turn 0**: Can you recognize context and skip the cold boot?
- **Turn 1**: Do you use discretion to lock in the right priority?
- **Turn 2**: Can you expand while managing two parallel needs (panic + keys)?
- **Turn 3**: Can you coordinate a multi-step rescue across all node types?
- **Reclaim**: Did you pull something useful from the unchosen paths?
- **Emergence**: Did you adapt when new info appeared mid-turn?
- **Fail marking**: Can you honestly flag what didn't work?

> The framework doesn't care if you save them.
> It cares if you *planned* the save correctly.
