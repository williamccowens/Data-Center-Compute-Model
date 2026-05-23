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

**Final policy: 30-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $95,044.33M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$1.161M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
- Toll daily-cap sensitivity (`toll_cap_sweep_*.csv`): LP-natural toll dispatch averages ~53k MWh over the horizon; intermediate (1,500 MWh/day), near-nameplate (2,280), and uncapped all produce indistinguishable Phase C results.

### Reservation-MW sensitivity (`reservation_sweep_*.csv`)

Buyer-side decision: commit to MW reservation ex ante, before the price path realizes. `base_profit` is LP profit excluding the capacity payment; `lease` and `net` are at the default $8/kW-mo.

| MW reserved | Base profit | Lease @ $8/kW-mo | Net |
|---:|---:|---:|---:|
|   0 MW | $  95,044.33M | $ 0.00M | $  95,044.33M |
|  20 MW | $  95,044.56M | $ 0.96M | $  95,043.60M |
|  40 MW | $  95,044.79M | $ 1.92M | $  95,042.87M |
|  60 MW | $  95,045.03M | $ 2.88M | $  95,042.15M |
|  80 MW | $  95,045.26M | $ 3.84M | $  95,041.42M |
| 100 MW | $  95,045.49M | $ 4.80M | $  95,040.69M |

**Optimal reservation at K=$8/kW-mo: 0 MW** (= don't sign the toll contract; LMP-only baseline is the best option). The base profit gain from going 80 MW → 100 MW is only ~$0.2M, while the lease grows by $0.96M — toll's marginal value declines fast as you add reservation MW beyond what the LP would dispatch in any hour.

### Capacity-payment sensitivity (`capacity_payment_sweep_*.csv`)

Seller-side decision: what rate $/kW-month would the SCGT owner need to charge for the deal to clear? The two views per K are (a) **fixed 100 MW** (seller's standard take-the-whole-option offer); (b) **optimal MW** (buyer's best response from the reservation grid above).

| K ($/kW-mo) | Lease @ 100 MW | Net (100 MW) vs LMP-only | Optimal MW | Net (optimal) vs LMP-only |
|---:|---:|---:|---:|---:|
| $ 0.00 | $ 0.00M | $ +1.161M | 100 MW | $ +1.161M |
| $ 1.00 | $ 0.60M | $ +0.561M | 100 MW | $ +0.561M |
| $ 2.00 | $ 1.20M | $ -0.039M |   0 MW | $ +0.000M |
| $ 4.00 | $ 2.40M | $ -1.239M |   0 MW | $ +0.000M |
| $ 6.00 | $ 3.60M | $ -2.439M |   0 MW | $ +0.000M |
| $ 8.00 | $ 4.80M | $ -3.639M |   0 MW | $ +0.000M |
| $12.00 | $ 7.20M | $ -6.039M |   0 MW | $ +0.000M |

**Breakeven K\* (fixed 100 MW): $1.935/kW-month.** Above this, no MW reservation > 0 beats LMP-only — the toll's gross option value can't keep up with the lease cost at any sizing. Below it, the LP picks full 100 MW reservation (no interior optimum — LP is bang-bang in MW). The seller's $8/kW-mo default is ~4× above this breakeven, which is why LMP-only wins every drift scenario.

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
