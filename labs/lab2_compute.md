# Lab 2 — The power envelope

**Question:** how much inference can this spacecraft actually afford?

**Time:** ~50 min · **Tool:** `orbitplan`

---

## The number everyone gets wrong

Vendor TOPS figures are peak, synthetic, and unreachable in practice. Real
sustained utilisation on a non-trivial model is commonly 30–50% of peak. If you
size a mission on datasheet TOPS you will be out by 2–3× before you start.

```python
import orbitplan as op

acc = op.Accelerator.preset("jetson_agx_orin")   # 275 TOPS, 60 W
print(f"peak      : {acc.tops:.0f} TOPS")
print(f"effective : {acc.effective_ops_per_s/1e12:.0f} TOPS at {acc.utilization:.0%}")
print(f"efficiency: {acc.ops_per_joule/1e12:.2f} Tops/J")
```

## 2.1 Energy per inference

```python
import orbitplan as op

acc = op.Accelerator.preset("jetson_agx_orin")
for name in ["resnet50", "vit_b16", "yolov8m", "sar_segmenter"]:
    w = op.Workload.preset(name, input_mb=1, output_mb=0.01)
    print(f"{name:15s} {w.gops:5.0f} GOPs -> {w.energy_j(acc)*1000:7.2f} mJ")
```

**Exercise.** A SAR segmenter costs ~109 mJ per inference. At 2,160 inferences a
day, what continuous power does that need? Compute it before reading on.

The answer is about **2.7 mW**. Not watts — milliwatts.

## 2.2 The finding that should reframe your thinking

For sensor-driven Earth-observation workloads, **inference energy is essentially
free.** The compute is not the problem. Run it:

```python
import orbitplan as op

plan = op.MissionPlan(
    sensor=op.Sensor(burst_gb_per_s=10, duty_cycle=0.002, name="SAR"),
    workload=op.Workload.preset("sar_segmenter", input_mb=800, output_mb=2),
    accelerator=op.Accelerator.preset("jetson_agx_orin"),
    power=op.PowerBudget(array_area_m2=8),
    thermal=op.ThermalBudget(radiator_area_m2=2),
    link=op.LinkBudget(band="x_band"),
)
r = plan.evaluate()
print(r.summary())
```

Note `compute needed` against `envelope`. The margin is enormous. This is the
quantitative case for processing onboard: you are spending milliwatts to avoid
downlinking terabytes.

## 2.3 Where power *does* bind

Sensor workloads are cheap because the instrument only produces so much data.
Continuously-served workloads are different — demand is set by requests, not by an
instrument:

```python
import orbitplan as op

plan = op.MissionPlan(
    sensor=None,
    demand_per_day=2.0e11,                    # 200B tokens/day
    workload=op.Workload.preset("llm_1b_token", input_mb=0.002, output_mb=0.002),
    accelerator=op.Accelerator.preset("nvidia_h100"),
    power=op.PowerBudget(array_area_m2=40),
    thermal=op.ThermalBudget(radiator_area_m2=1.5),
    link=op.LinkBudget(band="optical"),
)
print(plan.evaluate().summary())
```

**Exercise.** The verdict is `thermal`, not `power` — the 40 m² array makes
7.4 kW while the 1.5 m² radiator caps compute at 773 W. Grow the radiator until
the bottleneck moves to `power`. What area does that take, and what does that mass
do to your launch cost (use `orbitherm` from Lab 1)?

This is Lab 1's lesson appearing again from the other side: **thermal binds before
power almost every time.**

## 2.4 Read the power budget honestly

```python
import orbitplan as op

pb = op.PowerBudget(array_area_m2=8)
print(f"peak (sunlit)     : {pb.peak_w:7.0f} W")
print(f"orbit average     : {pb.orbit_average_w:7.0f} W")
print(f"available to compute: {pb.compute_w:7.0f} W")
```

Peak to usable is roughly a 2× haircut: eclipse fraction, battery round-trip,
distribution losses, and the bus taking its share first. **Quoting array peak power
as if it were compute power is the second most common error in this field.**

## Checkpoint

You can now size an accelerator against a real power budget, and you know that for
EO workloads compute is nearly free while thermal is the wall. Next: whether the
results can actually get home.

→ [Lab 3: Getting data home](lab3_downlink.md)
