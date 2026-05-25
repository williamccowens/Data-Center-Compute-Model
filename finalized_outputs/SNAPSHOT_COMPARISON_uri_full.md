# Snapshot comparison (stress overlay = `uri_full`)

Cross-scenario view of the four 50-path Monte Carlo drift scenarios committed under `finalized_outputs/` (stress overlay = `uri_full`). Each snapshot is the same model under a different gas / power forward-curve overlay. For a downloadable version that pastes cleanly into Word or Google Docs, open [`SNAPSHOT_COMPARISON_uri_full.html`](./SNAPSHOT_COMPARISON_uri_full.html).

## Headline profit & winners

Top-line numbers per snapshot. 'Cadence profit' is the mean over 50 paths at the winning cadence. 'Breakeven K\*' is the capacity payment ($/kW-mo) at which fixed-100 MW Houston tolling stops beating LMP-only (linearly interpolated from the K sweep).

| Snapshot | Gas drift | Power drift | Cadence winner | Cadence profit | Δ vs baseline | Full-cost proc. winner | Variable-cost proc. winner | VC gap ($M) | Breakeven K* |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | +0.0% | +0.0% | 90d | $36,363.99M | +0.00 | LMP + toll | LMP + toll + BESS both | +9.12 | $11.781/kW-mo |
| ai_structural | +0.5% | +1.0% | 90d | $36,363.67M | -0.32 | LMP + toll | LMP + toll + BESS both | +9.15 | $11.872/kW-mo |
| mild_drift | +3.0% | +1.5% | 90d | $36,363.46M | -0.53 | LMP + toll | LMP + toll + BESS both | +9.17 | $11.835/kW-mo |
| ai_plus_brent | +6.5% | +4.0% | 90d | $36,362.62M | -1.37 | LMP + toll | LMP + toll + BESS both | +9.25 | $11.981/kW-mo |

## Procurement Δ vs LMP-only across snapshots

Each cell is the procurement scenario's mean profit minus the LMP-only mean profit *within the same snapshot* ($M, both over 50 paths). Negative = the scenario underperforms LMP-only in that drift overlay. The corresponding heatmap is in [`comparison_figures/procurement_heatmap.png`](./comparison_figures_uri_full/procurement_heatmap.png).

| Scenario | baseline | ai_structural | mild_drift | ai_plus_brent |
|:---|---:|---:|---:|---:|
| LMP + toll | +2.27 | +2.32 | +2.30 | +2.39 |
| LMP + BESS Houston | -0.98 | -0.96 | -0.95 | -0.91 |
| LMP + BESS West | -0.71 | -0.69 | -0.68 | -0.64 |
| LMP + BESS both | -1.68 | -1.65 | -1.63 | -1.55 |
| LMP + toll + BESS Houston | +1.29 | +1.36 | +1.35 | +1.48 |
| LMP + toll + BESS West | +1.56 | +1.63 | +1.62 | +1.75 |
| LMP + toll + BESS both | +0.58 | +0.67 | +0.67 | +0.84 |

## Sweep-curve overlays

- **Capacity-payment sweep** — [`comparison_figures_uri_full/cap_payment_overlay.png`](./comparison_figures_uri_full/cap_payment_overlay.png). Δ vs LMP-only at 100 MW reservation as K rises. Steeper-positive snapshots (more drift) push the breakeven K\* rightward.
- **Reservation-MW sweep** — [`comparison_figures_uri_full/reservation_overlay.png`](./comparison_figures_uri_full/reservation_overlay.png). Each curve is the net at default $8/kW-mo minus that snapshot's own 0-MW point, so the shapes (concavity, monotonicity) are directly comparable across drift levels.
- **Toll daily-cap sweep** — [`comparison_figures_uri_full/toll_cap_grouped.png`](./comparison_figures_uri_full/toll_cap_grouped.png). Grouped bars: bracket × snapshot, Δ vs LMP-only ($M).
