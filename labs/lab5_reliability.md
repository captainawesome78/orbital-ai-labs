# Lab 5 — Staying correct

**Question:** does the answer survive a cosmic ray?

**Time:** ~45 min · **Tool:** `radshield`

---

## The failure nobody instruments for

Labs 1–4 assumed the hardware computes what you asked. Outside the magnetosphere
that assumption is weaker than you'd like. A single-event upset flips one bit in
memory. Commodity accelerators — the kind now being flown precisely because they're
cheap and fast — do not have ECC on every path.

The nasty part is *which* bit. Flip a mantissa bit and a weight moves slightly.
Flip a high exponent bit and 0.01 becomes 1e30. Your model keeps running, produces
confident garbage, and nothing raises an error.

## 5.1 Watch a single bit ruin a weight

```python
import numpy as np
import radshield as rs

w = np.array([0.01], dtype=np.float32)
for bit in [0, 5, 15, 23, 30]:
    flipped = rs.inject.flip_bits_at(w.copy(), np.array([0]), bit=bit)
    print(f"bit {bit:2d} -> {flipped[0]:.6g}")
```

**Exercise.** Which bits are harmless and which are catastrophic? Map the boundary.
Then consider: your weights are ~32 million bits per 1M-parameter layer, and the
exponent bits are ~25% of them.

## 5.2 Detect and repair

`WeightGuard` checksums your parameters and keeps a golden copy.

```python
import numpy as np
import radshield as rs

rng = np.random.default_rng(0)
params = {"W1": rng.normal(0, 0.1, (64, 64)).astype(np.float32)}

guard = rs.WeightGuard(params)
print(f"before  max|w| = {np.abs(params['W1']).max():.4f}")

params["W1"] = rs.inject.inject_bit_flips(
    params["W1"], n_flips=5, rng=np.random.default_rng(1))
print(f"corrupt max|w| = {np.abs(params['W1']).max():.4g}")

repaired = guard.verify_and_repair(params)
print(f"repaired {repaired} array(s)")
print(f"after   max|w| = {np.abs(params['W1']).max():.4f}")
```

**Exercise.** Raise `n_flips` and find where repair stops keeping up. You will not find
it: `WeightGuard` restores wholesale from a golden copy rather than correcting errors,
so it survives every element of the array being corrupted.

The real limits are elsewhere, and they are the ones to take to a design review. The
golden copy doubles your weight memory — mass, power, launch cost. The copy sits in the
same radiation environment and is not itself protected. And corruption between two
checks is never flagged, so the tunable that matters is check *frequency*, traded
against the compute cost of checksumming.

(SEU rates vary by orders of magnitude between benign LEO and a South Atlantic Anomaly
pass — this is where you need real radiation-environment data, not a default.)

## 5.3 Contain what you can't repair

Weights aren't the only thing that flips. Activations get corrupted too, and there
is no golden copy to restore. Clamp instead:

```python
import numpy as np
import radshield as rs

clean = np.random.default_rng(0).normal(0, 1, 500).astype(np.float32)
sanitize = rs.OutputSanitizer.from_calibration(clean, margin=4.0)

corrupted = np.array([1e30, -1e30, np.nan, 0.5], dtype=np.float32)
print("in :", corrupted)
print("out:", sanitize(corrupted))
```

Note NaN → 0 and the explosions clamped to the calibrated envelope. The model
degrades instead of producing nonsense.

**Exercise.** Vary `margin`. Too tight and you clip legitimate outliers; too loose
and you pass corruption through. Where would you set it for a classifier whose
output feeds an autonomous tasking decision?

## 5.4 The gotcha: this changes your power budget

Protection isn't free. Checksums cost compute, and the golden copy costs memory —
which costs mass, which costs launch.

**Exercise.** Return to Lab 2. If radiation protection adds 15% compute overhead,
recompute your inferences-per-day. The EO case absorbs it without noticing — 15% of
2.73 mW is 0.41 mW. The LLM-serving case does not change its *verdict* either; it was
thermal-bound before and stays thermal-bound. What changes is the outcome: at a fixed
773 W ceiling, 15% more compute per inference is 13% fewer tokens served.

A bottleneck that does not move is not the same as an overhead that does not cost you,
and the summary line only shows you the first. **Reliability engineering has to be in
the power budget from the start, not bolted on after the design closes.**

## Checkpoint

You can now argue that an orbital inference design is not just feasible and
economic but *correct* — and you know why a design review that never mentions
single-event upsets is incomplete.

→ [Capstone](capstone.md)
