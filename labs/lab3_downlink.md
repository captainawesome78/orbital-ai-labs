# Lab 3 — Getting data home

**Question:** poes the result fit through the link, and does a laser mesh rescue it?

**Time:** ~50 min · **Tool:** `orbitplan`

---

## Contact time is the scarce resource

A LEO satellite sees a given ground station for roughly 8 usable minutes, about 5
times a day. That is ~40 minutes of contact out of 1,440. Everything else about
your downlink budget follows from that.

```python
import orbitplan as op

for band in ["s_band", "x_band", "ka_band", "optical"]:
    lb = op.LinkBudget(band=band)
    print(f"{band:9s} {lb.rate_bps/1e6:8.0f} Mbps -> {lb.gb_per_day:9.1f} GB/day")
```

## 3.1 The SAR problem

A SAR instrument imaging just 0.2% of the time produces 1,728 GB/day.

```python
import orbitplan as op

sensor = op.Sensor(burst_gb_per_s=10, duty_cycle=0.002)
link = op.LinkBudget(band="x_band")
print(f"generated : {sensor.gb_per_day:,.0f} GB/day")
print(f"X-band    : {link.gb_per_day:,.0f} GB/day")
print(f"shortfall : {sensor.gb_per_day/link.gb_per_day:,.0f}x")
```

**Exercise.** How many passes per day would you need to downlink it raw? Try
`op.LinkBudget(band="x_band", passes_per_day=N)` and solve for N. Then ask whether
that many ground stations is a business you want to be in.

## 3.2 Onboard inference as compression

The fix isn't a bigger pipe, it's sending less.

```python
import orbitplan as op

def run(output_mb, label):
    r = op.MissionPlan(
        sensor=op.Sensor(burst_gb_per_s=10, duty_cycle=0.002),
        workload=op.Workload.preset("sar_segmenter", input_mb=800, output_mb=output_mb),
        accelerator=op.Accelerator.preset("jetson_agx_orin"),
        power=op.PowerBudget(array_area_m2=8),
        thermal=op.ThermalBudget(radiator_area_m2=2),
        link=op.LinkBudget(band="x_band"),
    ).evaluate()
    print(f"{label:20s} {r.data_after_inference_gb_day:9.2f} GB/day -> {r.bottleneck}")

run(800, "raw downlink")       # no processing
run(2,   "onboard segmenter")  # 400x reduction
```

One satellite, one line changed, and the mission goes from impossible to feasible.
**This single comparison is the business case for onboard AI.** Keep it handy.

## 3.3 Does a laser mesh fix it?

Inter-satellite links are the fashionable answer. Test it:

```python
import orbitplan as op

for label, link in [
    ("direct X-band",          op.LinkBudget(band="x_band")),
    ("mesh 100 sats / 10 gs",  op.LinkBudget(band="x_band",
        relay=op.RelayLink(constellation_size=100, ground_stations=10))),
    ("mesh 20 sats / 30 gs",   op.LinkBudget(band="x_band",
        relay=op.RelayLink(constellation_size=20, ground_stations=30))),
]:
    extra = f" (limited by {link.relay.limiting_factor})" if link.relay else ""
    print(f"{label:24s} {link.gb_per_day:9.1f} GB/day{extra}")
```

**Exercise.** Inspect `link.relay.isl_limit_gb_per_day` versus
`link.relay.ground_share_gb_per_day` for the 100/10 case. Which one binds?

The crosslink could carry ~600,000 GB/day. The constellation's share of ten ground
stations is 622. **A mesh creates reach, not bandwidth.** Relaying through 100
satellites into 10 stations buys you a tenth of ten stations. If the ground segment
is thin, a mesh relocates your bottleneck rather than removing it.

This is the single most useful thing in this lab when someone pitches you a
crosslink constellation.

## 3.4 The trap

Note that the 100-satellite mesh raises capacity roughly 10× and the raw-downlink
case is *still* infeasible. Capacity improvements feel large and change nothing if
you're three orders of magnitude short. **Always compare against the requirement,
not against the previous number.**

## Checkpoint

You can size a link budget, quantify onboard inference as a compression ratio, and
evaluate a mesh claim on its merits. Next: whether any of this should be in orbit.

→ [Lab 4: Orbit or ground](lab4_placement.md)
