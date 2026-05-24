# Snapshot comparison

Cross-scenario view of the four 50-path Monte Carlo drift scenarios committed under `example_outputs_TEMPORARY/`. Each snapshot is the same model under a different gas / power forward-curve overlay. For a downloadable version that pastes cleanly into Word or Google Docs, open [`SNAPSHOT_COMPARISON.html`](./SNAPSHOT_COMPARISON.html).

## Headline profit & winners

Top-line numbers per snapshot. 'Cadence profit' is the mean over 50 paths at the winning cadence. 'Breakeven K\*' is the capacity payment ($/kW-mo) at which fixed-100 MW Houston tolling stops beating LMP-only (linearly interpolated from the K sweep).

| Snapshot | Gas drift | Power drift | Cadence winner | Cadence profit | Δ vs baseline | Full-cost proc. winner | Variable-cost proc. winner | VC gap ($M) | Breakeven K* |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | +0.0% | +0.0% | 95d | $148,101.32M | +0.00 | LMP only | LMP + toll + BESS both | +5.78 | $3.681/kW-mo |
| ai_structural | +0.5% | +1.0% | 95d | $148,101.00M | -0.32 | LMP only | LMP + toll + BESS both | +5.87 | $3.773/kW-mo |
| mild_drift | +3.0% | +1.5% | 95d | $148,100.79M | -0.53 | LMP only | LMP + toll + BESS both | +5.86 | $3.737/kW-mo |
| ai_plus_brent | +6.5% | +4.0% | 95d | $148,099.94M | -1.38 | LMP only | LMP + toll + BESS both | +6.04 | $3.885/kW-mo |

## Procurement Δ vs LMP-only across snapshots

Each cell is the procurement scenario's mean profit minus the LMP-only mean profit *within the same snapshot* ($M, both over 50 paths). Negative = the scenario underperforms LMP-only in that drift overlay. The corresponding heatmap is in [`comparison_figures/procurement_heatmap.png`](./comparison_figures/procurement_heatmap.png).

| Scenario | baseline | ai_structural | mild_drift | ai_plus_brent |
|:---|---:|---:|---:|---:|
| LMP + toll | -2.59 | -2.54 | -2.56 | -2.47 |
| LMP + BESS Houston | -1.35 | -1.33 | -1.32 | -1.28 |
| LMP + BESS West | -1.08 | -1.06 | -1.05 | -1.01 |
| LMP + BESS both | -2.43 | -2.40 | -2.38 | -2.29 |
| LMP + toll + BESS Houston | -3.94 | -3.87 | -3.88 | -3.75 |
| LMP + toll + BESS West | -3.67 | -3.60 | -3.61 | -3.48 |
| LMP + toll + BESS both | -5.02 | -4.93 | -4.94 | -4.76 |

## Sweep-curve overlays

- **Capacity-payment sweep** — [`comparison_figures/cap_payment_overlay.png`](./comparison_figures/cap_payment_overlay.png). Δ vs LMP-only at 100 MW reservation as K rises. Steeper-positive snapshots (more drift) push the breakeven K\* rightward.
- **Reservation-MW sweep** — [`comparison_figures/reservation_overlay.png`](./comparison_figures/reservation_overlay.png). Each curve is the net at default $8/kW-mo minus that snapshot's own 0-MW point, so the shapes (concavity, monotonicity) are directly comparable across drift levels.
- **Toll daily-cap sweep** — [`comparison_figures/toll_cap_grouped.png`](./comparison_figures/toll_cap_grouped.png). Grouped bars: bracket × snapshot, Δ vs LMP-only ($M).
