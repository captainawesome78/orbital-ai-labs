# Capstone — Design a mission

**Time:** ~2 hours · **Tools:** all three

---

## The brief

A customer wants to detect illegal fishing vessels worldwide, near-real-time. They
have a SAR constellation concept and want to know whether onboard AI makes sense,
what it costs, and what could go wrong.

Requirements:

- Global coverage, revisit under 6 hours
- Detection latency under 30 minutes from image capture
- SAR instrument: 10 GB/s while imaging, ~0.2% duty cycle per satellite
- Detection model: ~200 GOPs per scene, 800 MB in, ~2 MB of contacts out
- 5-year mission
- Customer has 3 ground stations and won't buy more

## Deliverable

A one-page recommendation containing:

1. **Thermal** — radiator area, mass, launch cost per satellite (Lab 1)
2. **Compute** — accelerator choice, sustained power, inferences/day (Lab 2)
3. **Downlink** — link budget; whether it closes with 3 stations; whether a
   crosslink mesh is worth the money (Lab 3)
4. **Placement** — orbit vs ground with numbers, and the crossover (Lab 4)
5. **Reliability** — SEU protection strategy and its budget cost (Lab 5)
6. **The honest risk** — what would make this recommendation wrong

## Constraints worth thinking about

- Latency under 30 minutes is doing a lot of work here. Downlinking raw and
  processing on the ground means waiting for a pass. What does that do to the
  requirement?
- Three ground stations is a hard constraint. Compute the shared capacity before
  assuming a mesh saves you.
- The customer will ask "why not just use more ground stations?" Have the number.

## Suggested skeleton

```python
import orbitherm as ot
import orbitplan as op

sensor = op.Sensor(burst_gb_per_s=10, duty_cycle=0.002, name="SAR")
workload = op.Workload.preset("sar_segmenter", input_mb=800, output_mb=2)
accel = op.Accelerator.preset("jetson_agx_orin")

# 1. thermal — size it, then feed the area back in
sizing = ot.size_radiator(accel.watts, target_temp_c=50)

# 2-3. feasibility
plan = op.MissionPlan(
    sensor=sensor, workload=workload, accelerator=accel,
    power=op.PowerBudget(array_area_m2=...),
    thermal=op.ThermalBudget(radiator_area_m2=sizing["area_m2"]),
    link=op.LinkBudget(band="x_band", passes_per_day=...),
)

# 4. economics
placement = op.compare_placement(
    workload=workload,
    inferences_per_day=sensor.gb_per_day * 1000 / workload.input_mb,
    data_gb_per_day=sensor.gb_per_day,
    link=plan.link,
)
```

## What a good answer looks like

It states a recommendation, backs each claim with a number the reader can
reproduce, and is explicit about which inputs would flip the conclusion. It does
**not** conclude "orbit wins" because that's the fashionable answer — it concludes
whatever the arithmetic says, and shows the arithmetic.

If your recommendation doesn't include at least one number that surprised you,
you probably haven't pushed on it hard enough.

---

## Where to go next

- Override every default with real vendor and contract numbers. The defaults are
  public list rates and they date fast.
- The models are first-order. Before flight, this needs detailed thermal analysis,
  proper orbital mechanics, and radiation qualification against your actual parts.
- If you extend the tools, they're Apache-2.0:
  [orbitherm](https://github.com/captainawesome78/orbitherm) ·
  [orbitplan](https://github.com/captainawesome78/orbitplan) ·
  [radshield](https://github.com/captainawesome78/radshield)
