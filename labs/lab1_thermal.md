# Lab 1 — The cooling wall

**Question:** can the spacecraft shed the heat this compute makes?

**Time:** ~45 min · **Tool:** `orbitherm`

---

## Why this is first

The intuition most people bring from datacentres is that power is the constraint.
In orbit it usually isn't. Solar power is comparatively easy to add — you unfold
more array. Getting rid of the resulting heat is not, because in vacuum there is
nothing to convect into. Heat leaves only by radiation:

```
q = ε σ T⁴          W/m² radiated from a surface
```

Radiative capacity grows as T⁴, which sounds generous until you notice you can't
run the hardware hot. Cap the radiator at 50 °C and each square metre sheds only a
few hundred watts. So radiator **area** — and therefore mass, and therefore launch
cost — is what actually binds.

## 1.1 Feel the numbers

```python
from orbitherm import physics as p

for t_c in [0, 27, 50, 77, 100]:
    q = p.radiative_flux(p.c_to_k(t_c), emissivity=0.85)
    print(f"{t_c:3d} °C -> {q:6.1f} W/m²")
```

Expected:

```
  0 °C ->  268.3 W/m²
 27 °C ->  391.2 W/m²
 50 °C ->  525.6 W/m²
 77 °C ->  724.5 W/m²
100 °C ->  934.5 W/m²
```

**Read this carefully.** At a radiator temperature you can actually hold, you get
roughly 500 W per square metre. A single 700 W H100 therefore needs more than a
square metre of radiator *just for itself* — before you account for the sunlight
falling on that radiator.

## 1.2 Size a real payload

```python
import orbitherm as ot

for kw in [1, 10, 100, 1000]:
    s = ot.size_radiator(kw * 1000, target_temp_c=50)
    print(f"{kw:5d} kW -> {s['area_m2']:8.1f} m²  "
          f"{s['mass_kg']:8.0f} kg  ${s['launch_cost_today_usd']/1e6:6.2f}M")
```

**Exercise.** Before running it: guess the radiator area for 1 MW. Most people
guess low by an order of magnitude.

The 1 MW answer is about **1,940 m²**. For scale: the ISS's entire deployed
radiator suite — photovoltaic and heat-rejection combined — is roughly 6,500 ft²,
about 600 m². So cooling **one megawatt** of orbital compute needs on the order of
**three ISS radiator suites**.

Now scale that mentally to the gigawatt-class orbital datacentres in press
releases. This is the core physical objection to the whole thesis, and you just
derived it in four lines of code.

## 1.3 Orientation is not a detail

A radiator pointed at the Sun absorbs heat instead of rejecting it.

```python
from orbitherm import physics as p

for orient in ["deep_space", "nadir", "sun_facing"]:
    env = p.environmental_flux(orient, emissivity=0.85)
    print(f"{orient:12s} absorbs {env:6.1f} W/m²")
```

**Exercise.** Take the 100 kW payload from 1.2. Compute the required area for each
orientation using `p.required_area(power_w, target_temp_c, emissivity, env_flux)`.
Sun-facing needs roughly twice the area of the deep-space case — an attitude
constraint that silently doubles your radiator mass.

## 1.4 Evaluate a complete design

```python
import orbitherm as ot

twin = ot.ThermalTwin(
    power_w=100_000,
    radiator=ot.Radiator(area_m2=200, orientation="deep_space"),
    orbit=ot.Orbit(altitude_km=550),
)
r = twin.evaluate()
print(r.verdict, "|", r.message)
```

**Exercise.** Shrink the radiator until the verdict flips to `marginal`, then to
`infeasible`. Note the area at each transition. That number — the minimum viable
radiator for your payload — is the one to bring to a design review.

## 1.5 The gotcha: eclipse doesn't help as much as you'd think

Spacecraft spend ~37% of a LEO orbit in shadow, so you might expect a cooling
break. Run the transient:

```python
import orbitherm as ot

twin = ot.ThermalTwin(
    power_w=100_000,
    radiator=ot.Radiator(area_m2=200, orientation="deep_space"),
    orbit=ot.Orbit(altitude_km=550),
)
for pt in twin.transient(steps=8):
    print(f"t={pt['t_s']/60:5.1f} min  {pt['temp_c']:5.1f} °C  "
          f"{'sun' if pt['sunlit'] else 'eclipse'}")
```

The temperature barely moves. Radiator thermal mass dominates over a 95-minute
orbit, and your compute is still dissipating during eclipse. **Do not size a
radiator on the assumption that eclipse gives you thermal headroom.**

## Checkpoint

You should now be able to state, for any proposed payload: the radiator area, its
mass, its launch cost, and whether the design closes. If someone shows you an
orbital datacentre concept, your first question is now *"how big is the radiator?"*

→ [Lab 2: The power envelope](lab2_compute.md)
