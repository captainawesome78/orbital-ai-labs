# Sizing AI for Orbit

**A hands-on curriculum for engineers who have to make AI actually work in space.**

Most material on orbital compute is either spacecraft-systems coursework that never
mentions inference, or AI coursework that assumes infinite power and a fat network.
The gap is the practitioner skill in between: *given a model and a satellite, does
this close?* — and if not, which of the four walls you hit first.

You will finish able to answer, with numbers:

- How big a radiator does this payload need, and what does that mass cost to launch?
- How many inferences a day can this spacecraft actually afford?
- Will the results fit through the downlink — and does a laser mesh rescue it?
- Should this run in orbit at all, or should you downlink and use a cloud?
- Will the answer still be correct after a cosmic ray flips a bit in your weights?

Every lab is runnable. No simulators to install, no accounts to create.

## Who this is for

Engineers at EO operators, orbital-compute startups and defence primes who have to
size or defend an onboard-AI design. Also useful if you're evaluating someone else's
orbital compute claims and want to check the arithmetic yourself.

Assumed: comfortable Python, basic ML familiarity. **Not** assumed: any spacecraft
engineering background. The physics is introduced where it's needed.

## Setup

```bash
pip install orbitherm orbitplan radshield
```

Three open-source packages, no other dependencies. Verify:

```bash
python -c "import orbitherm, orbitplan, radshield; print('ready')"
```

## The curriculum

| Lab | Question it answers | Tool |
|---|---|---|
| [1. The cooling wall](labs/lab1_thermal.md) | Can the spacecraft shed the heat this compute makes? | `orbitherm` |
| [2. The power envelope](labs/lab2_compute.md) | How much inference can it actually afford? | `orbitplan` |
| [3. Getting data home](labs/lab3_downlink.md) | Does the result fit the link? Does a mesh help? | `orbitplan` |
| [4. Orbit or ground](labs/lab4_placement.md) | Should this be in orbit at all? | `orbitplan` |
| [5. Staying correct](labs/lab5_reliability.md) | Does it survive radiation-induced bit flips? | `radshield` |
| [Capstone](labs/capstone.md) | Design and defend a complete mission | all three |

Roughly 45–60 minutes per lab. Work them in order — each builds on the last, and the
capstone assumes all five.

## The four walls

The organising idea. An orbital inference design has to clear four independent
constraints, and optimising one in isolation is how these plans die:

1. **Thermal** — in vacuum heat leaves only by radiation, so radiator area (not
   power) is usually the binding constraint on dense compute.
2. **Power** — solar array output after eclipse, battery and distribution losses,
   minus what the bus already takes.
3. **Downlink** — contact time is billed by the minute and rationed by orbital
   geometry. Past a few GB/day, downlinking raw data stops being expensive and
   starts being impossible.
4. **Correctness** — a single-event upset in a weight can turn 0.01 into 1e30, and
   nothing downstream will tell you it happened.

Labs 1–4 cover walls 1–3 plus the economics. Lab 5 covers wall 4.

## Interactive companions

Each lab has a browser version if you'd rather explore before coding:

- [Thermal Twin](https://captainawesome78.github.io/orbital-thermal-twin/) — Lab 1
- [Feasibility Planner](https://captainawesome78.github.io/orbital-thermal-twin/planner.html) — Labs 2–3
- [Orbit or Ground?](https://captainawesome78.github.io/orbital-thermal-twin/placement.html) — Lab 4

## Scope and honesty

These are first-order engineering models — the right tool for architecture trade
studies, go/no-go calls and sanity-checking vendor claims. They are **not** a
substitute for detailed thermal CAD, STK-grade orbital analysis, or radiation
qualification. Assumptions (circular LEO, β=0 eclipse geometry, isothermal
radiators, public list pricing) are stated in each lab and every one is overridable.

Where a number is uncertain, the labs say so. Where the model would mislead you,
the labs point at it.

## License

Apache-2.0. Use it, fork it, teach from it.
