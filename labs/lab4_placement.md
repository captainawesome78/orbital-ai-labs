# Lab 4 — Orbit or ground

**Question:** should this run in orbit at all?

**Time:** ~45 min · **Tool:** `orbitplan`

---

## The question the engineering doesn't answer

Labs 1–3 tell you whether a design *closes*. They say nothing about whether you
*should* build it. A design can be perfectly feasible and still be a worse idea
than downlinking everything and renting a GPU.

The comparison hinges on an asymmetry that is easy to miss:

- Process **in orbit** → you downlink a *result*.
- Process **on the ground** → you must first downlink *everything*.

And ground-station time is billed by the minute and rationed by orbital geometry.

## 4.1 The SAR case

```python
import orbitplan as op

r = op.compare_placement(
    workload=op.Workload.preset("sar_segmenter", input_mb=800, output_mb=2),
    inferences_per_day=2160,
    data_gb_per_day=1728,
    link=op.LinkBudget(band="x_band"),
)
print(r.summary())
```

**Exercise.** Before running: guess the daily cost of each option.

Look at `ground_contact_hours_needed` against `ground_contact_hours_available`.
The ground option needs 16 hours of contact per day and has 0.67. It isn't
expensive — it's **impossible**. Onboard processing here isn't the cheaper option,
it's the only one that exists.

## 4.2 Where orbit loses

The tool is not a shill for orbit. Push the volume down:

```python
import orbitplan as op

r = op.compare_placement(
    workload=op.Workload.preset("resnet50", input_mb=6, output_mb=0.005),
    inferences_per_day=833,
    data_gb_per_day=5,
    link=op.LinkBudget(band="x_band"),
)
print(r.winner, "|", r.message)
```

At 5 GB/day there isn't enough data to justify amortising $65,000 of hardware and
launch. Downlink it and use the cloud.

**Exercise.** Find your crossover. Sweep `data_gb_per_day` and locate where
`r.winner` flips. Then change `OrbitOption(payload_mass_kg=..., hardware_usd=...)`
and watch it move. Cheaper launch pushes the crossover down — which is precisely
why launch cost is the variable the whole orbital-compute thesis rests on.

```python
import orbitplan as op

link = op.LinkBudget(band="x_band")
for gb in [1, 5, 10, 50, 200, 1000]:
    n = gb * 1000 / 800
    r = op.compare_placement(
        workload=op.Workload.preset("sar_segmenter", input_mb=800, output_mb=2),
        inferences_per_day=n, data_gb_per_day=gb, link=link)
    flag = "" if r.ground_feasible else "  (ground impossible)"
    print(f"{gb:6.0f} GB/day  ground ${r.ground_total_usd_day:9,.2f}  "
          f"orbit ${r.orbit_total_usd_day:7,.2f}  -> {r.winner}{flag}")
```

## 4.3 When price stops mattering

Some data can't legally or contractually transit third-party ground stations.

```python
import orbitplan as op

r = op.compare_placement(
    workload=op.Workload.preset("resnet50", input_mb=6, output_mb=0.005),
    inferences_per_day=833, data_gb_per_day=5,
    link=op.LinkBudget(band="x_band"),
    data_must_stay_onboard=True,
)
print(r.message)
```

Note it reports the **premium you're paying**, not a pretence that the compliant
option is also the cheap one. When you present a sovereignty-driven architecture,
quantifying that premium is what makes the recommendation credible.

## 4.4 The gotcha: your prices are stale

```python
import orbitplan as op

r = op.compare_placement(
    workload=op.Workload.preset("sar_segmenter", input_mb=800, output_mb=2),
    inferences_per_day=2160, data_gb_per_day=1728,
    link=op.LinkBudget(band="x_band"),
    ground=op.GroundOption(station_usd_per_min=3.0),      # reserved narrowband
    orbit=op.OrbitOption(launch_usd_per_kg=200.0),        # target launch cost
)
print(r.summary())
```

Defaults are public list rates that date within months. **Always override them with
your actual contracted numbers before quoting a result to anyone.** A model with
someone else's prices in it is a talking point, not an analysis.

## Checkpoint

You can now argue orbit-versus-ground with numbers instead of vibes, in both
directions, and you know which input to attack when someone else's answer looks
wrong.

→ [Lab 5: Staying correct](lab5_reliability.md)
