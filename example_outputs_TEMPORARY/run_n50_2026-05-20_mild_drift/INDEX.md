# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-20_baseline/INDEX.md` — placeholder
hardware throughputs, token decay halflife, BESS lease amortization, and
the DAM-as-RT proxy are unchanged. Read absolute figures as directional.

---

# Run bundle: 50-path Monte Carlo, mild Brent-shock overlay

**Date:** 2026-05-20
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas **+3.0 %**, power **+1.5 %**
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `971e914` (Add plots.py + baseline n=50 snapshot)

Companion to `../run_n50_2026-05-20_baseline/` (gas/power = 0/0). Same
seed → same MC innovations; the only thing that differs is the OU
long-run mean of HH and ERCOT LMP.

**Scenario framing.** The +3 % HH / +1.5 % LMP overlay is roughly half of
a full "geopolitical Brent shock" scenario — anchored against the May-2026
EIA STEO Brent forecast (Brent peaks $115/b in 2Q 2026 under continued
Strait of Hormuz disruption, an implied ~+15 % move vs the 2025 average).
Pass-through into US gas and ERCOT power via the documented elasticities:

- Brent → Henry Hub ≈ 0.2 (LNG-export pull at ~18 Bcf/d running capacity)
- Henry Hub → ERCOT LMP ≈ 0.5 (gas-on-margin pass-through)

So a +15 % Brent overlay translates to roughly `--gas-drift-pct 0.03
--power-drift-pct 0.015`. The full +30 % Brent shock scenario would be
`--gas-drift-pct 0.06 --power-drift-pct 0.03`.

This snapshot is the Brent-shock variant only; the secular "AI data-center
load growth" story (ERCOT CDR / EIA AEO 2026 demand forecast) is captured
separately in `../run_n50_2026-05-20_ai_structural/` and combined with the
full Brent shock in `../run_n50_2026-05-20_ai_plus_brent/`.

---

## Headline result

**Final policy: 30-day cadence × (LMP + Houston tolling, no BESS) → mean profit $95,045.49M / 6 months across 50 paths.**

**Profit delta vs the zero-drift baseline (`run_n50_2026-05-20_baseline`): -$0.56M** — essentially rounding error vs the $95B headline. The drift overlay does not change the policy decision:

- Same cadence winner (30d, confirmed under Phase C)
- Same procurement winner (LMP + Houston toll, no BESS)
- Toll value still ~$1.16M / 6mo (vs $1.14M baseline) — tiny lift from the bump in HH widening the LMP-vs-toll spread on the marginal hour

**Mechanism of the -$0.56M delta** (LMP does **not** affect inference revenue — token prices are decoupled from grid prices):

| Component | Driver | Magnitude |
|---|---|---|
| Power cost on LMP grid draw | +1.5 % × ~$35 avg LMP × 876,000 grid-MWh | ≈ +$440K cost |
| Toll cost (HH bump) | +3 % × ~$57 avg toll cost × 53,000 toll-MWh | ≈ +$90K cost |
| Inference revenue | **Unchanged** — depends on token prices, not LMP | $0 |
| BESS sell-to-grid revenue / charge cost | n/a — Phase C dropped BESS | $0 |
| **Net** | | **≈ −$0.5M (matches observed −$0.56M)** |

---

## Figures (`figures/`)

Same four charts as the baseline snapshot (`01_train_inf_diurnal.png`,
`02_train_inf_cost_daily.png`, `03b_procurement_mix_daily.png`,
`04_lmp_toll_overlay.png`). Visual differences vs baseline are subtle —
the LMP / toll-cost overlay's average levels are lifted by ~$0.5–$1.7/MWh,
but the diurnal shape and procurement-mix pattern are visually identical
at this drift magnitude.

For side-by-side comparison, diff the corresponding files in
`../run_n50_2026-05-20_baseline/figures/`.

---

## Files

Same structure as the baseline snapshot. See
`../run_n50_2026-05-20_baseline/INDEX.md` § Files for full descriptions
of each CSV / JSON. The schemas are unchanged — only the underlying
numbers shift slightly to reflect the +3 % / +1.5 % drift.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.03 --power-drift-pct 0.015
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.03 --power-drift-pct 0.015
```
