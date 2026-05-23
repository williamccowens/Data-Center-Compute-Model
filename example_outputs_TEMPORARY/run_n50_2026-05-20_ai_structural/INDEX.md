# ⚠️ TEMPORARY EXAMPLE OUTPUTS — not final numbers

Same caveats as `../run_n50_2026-05-20_baseline/INDEX.md`.

---

# Run bundle: 50-path Monte Carlo, AI-structural load-growth drift

**Date:** 2026-05-20
**Horizon:** 2026-06-01 → 2026-12-01 (6 months, hourly)
**MC paths:** 50, seed=42, doc_blended token-multiplier scheme
**Forward-curve drift:** gas **+0.5 %**, power **+1.0 %**
**Toll daily cap:** None (unconstrained)
**Branch / commit at time of run:** main @ `a17b23e` (Add mild_drift n=50 snapshot)

**Scenario framing.** Separate driver from the Brent/geopolitical
overlays. This run captures the *secular* load-growth story:
ERCOT data-center buildout is projected to push peak demand up ~5–7 %/yr
through 2030 (ERCOT CDR, Dec 2024), with EIA AEO 2026 implying roughly
+2 %/yr on average ERCOT LMP and +1 %/yr on Henry Hub from the resulting
power-balance tightening. Pro-rated to ~half a year for the
June–December 2026 horizon: `--gas-drift-pct 0.005 --power-drift-pct 0.01`.

Reading the four committed snapshots together:

| Snapshot | gas drift | power drift | Scenario |
|---|---|---|---|
| `baseline` | 0 % | 0 % | EIA STEO May-2026 short-term view, ~flat 2025→2026 |
| **`ai_structural` (this run)** | +0.5 % | +1.0 % | **EIA AEO + ERCOT CDR secular load-growth baseline** |
| `mild_drift` | +3.0 % | +1.5 % | ~half geopolitical Brent shock overlay |
| `ai_plus_brent` | +6.5 % | +4.0 % | Structural + full +30 % Brent shock (max-stress combined) |

---

## Headline result

**Final policy: 30-day training cadence × LMP-only (no Houston tolling, no BESS) → mean profit $95,044.52M / 6 months across 50 paths.**

- Phase A: 30d wins both stages; cadence-vs-cadence gaps remain ~$3B, dwarfing procurement gaps.
- Phase C: Gross Houston-toll option value (LP-derived, at full 100 MW reservation) = **$1.179M / 6mo** — well below the $4.8M default capacity payment ($8/kW-mo × 100 MW × 6 mo), so LMP-only wins. The toll value is independently corroborated by `ltemry/FTG-Final-Project`'s $1.42M HH-pricing estimate (~20% gap due to scope of cost calculation + price-proxy differences).
- Toll daily-cap sensitivity (`toll_cap_sweep_*.csv`): LP-natural toll dispatch averages ~53k MWh over the horizon; intermediate (1,500 MWh/day), near-nameplate (2,280), and uncapped all produce indistinguishable Phase C results.

### Reservation-MW sensitivity (`reservation_sweep_*.csv`)

Buyer-side decision: commit to MW reservation ex ante, before the price path realizes. `base_profit` is LP profit excluding the capacity payment; `lease` and `net` are at the default $8/kW-mo.

| MW reserved | Base profit | Lease @ $8/kW-mo | Net |
|---:|---:|---:|---:|
|   0 MW | $  95,044.52M | $ 0.00M | $  95,044.52M |
|  20 MW | $  95,044.76M | $ 0.96M | $  95,043.80M |
|  40 MW | $  95,044.99M | $ 1.92M | $  95,043.07M |
|  60 MW | $  95,045.23M | $ 2.88M | $  95,042.35M |
|  80 MW | $  95,045.46M | $ 3.84M | $  95,041.62M |
| 100 MW | $  95,045.70M | $ 4.80M | $  95,040.90M |

**Optimal reservation at K=$8/kW-mo: 0 MW** (= don't sign the toll contract; LMP-only baseline is the best option). The base profit gain from going 80 MW → 100 MW is only ~$0.2M, while the lease grows by $0.96M — toll's marginal value declines fast as you add reservation MW beyond what the LP would dispatch in any hour.

### Capacity-payment sensitivity (`capacity_payment_sweep_*.csv`)

Seller-side decision: what rate $/kW-month would the SCGT owner need to charge for the deal to clear? The two views per K are (a) **fixed 100 MW** (seller's standard take-the-whole-option offer); (b) **optimal MW** (buyer's best response from the reservation grid above).

| K ($/kW-mo) | Lease @ 100 MW | Net (100 MW) vs LMP-only | Optimal MW | Net (optimal) vs LMP-only |
|---:|---:|---:|---:|---:|
| $ 0.00 | $ 0.00M | $ +1.179M | 100 MW | $ +1.179M |
| $ 1.00 | $ 0.60M | $ +0.579M | 100 MW | $ +0.579M |
| $ 2.00 | $ 1.20M | $ -0.021M |   0 MW | $ +0.000M |
| $ 4.00 | $ 2.40M | $ -1.221M |   0 MW | $ +0.000M |
| $ 6.00 | $ 3.60M | $ -2.421M |   0 MW | $ +0.000M |
| $ 8.00 | $ 4.80M | $ -3.621M |   0 MW | $ +0.000M |
| $12.00 | $ 7.20M | $ -6.021M |   0 MW | $ +0.000M |

**Breakeven K\* (fixed 100 MW): $1.965/kW-month.** Above this, no MW reservation > 0 beats LMP-only — the toll's gross option value can't keep up with the lease cost at any sizing. Below it, the LP picks full 100 MW reservation (no interior optimum — LP is bang-bang in MW). The seller's $8/kW-mo default is ~4× above this breakeven, which is why LMP-only wins every drift scenario.

---

## Figures (`figures/`)

Same four charts as the baseline / mild_drift snapshots. Visual
differences between the three drift scenarios are subtle at this
magnitude.

---

## Files

Same structure as baseline. See `../run_n50_2026-05-20_baseline/INDEX.md` § Files for full descriptions.

---

## How to reproduce

```powershell
# from project root
python model\run_planning_doc.py --mc 50 --gas-drift-pct 0.005 --power-drift-pct 0.01
python model\power_procurement_sweep.py --mc 50 --toll-cap-sweep --gas-drift-pct 0.005 --power-drift-pct 0.01
```
