# Results tables — `run_n50_2026-05-23_ai_plus_brent`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,099.94M | $1.30M | $148,097.83M | $148,101.59M |
| 90d | $144,749.44M | $1.30M | $144,747.33M | $144,751.10M |
| 85d | $141,552.61M | $1.30M | $141,550.50M | $141,554.26M |
| 75d | $135,572.13M | $1.30M | $135,570.02M | $135,573.78M |
| 74d | $134,887.74M | $1.30M | $134,885.64M | $134,889.40M |
| 63d | $126,277.10M | $1.30M | $126,274.99M | $126,278.76M |
| 60d | $123,566.05M | $1.30M | $123,563.94M | $123,567.70M |
| 45d | $106,464.21M | $1.30M | $106,462.10M | $106,465.86M |
| 30d | $76,117.51M | $1.30M | $76,115.40M | $76,119.16M |
| 25d | $59,079.79M | $1.30M | $59,077.68M | $59,081.44M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $76,122.27M | $1.67M | $76,119.59M | $76,124.35M | +0.000 |
| LMP + BESS West | $76,121.27M | $1.59M | $76,118.72M | $76,123.21M | -1.008 |
| LMP + BESS Houston | $76,120.99M | $1.60M | $76,118.41M | $76,122.97M | -1.284 |
| LMP + BESS both | $76,119.98M | $1.52M | $76,117.54M | $76,121.83M | -2.292 |
| LMP + toll | $76,119.80M | $1.44M | $76,117.45M | $76,121.58M | -2.469 |
| LMP + toll + BESS West | $76,118.80M | $1.36M | $76,116.58M | $76,120.50M | -3.477 |
| LMP + toll + BESS Houston | $76,118.52M | $1.38M | $76,116.28M | $76,120.25M | -3.753 |
| LMP + toll + BESS both | $76,117.51M | $1.30M | $76,115.40M | $76,119.16M | -4.761 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.823M | $-4.492M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.151M | $0.973M | $-0.000M | $-0.000M | $-1.408M | $-3.000M |
| LMP + BESS West | $2.305M | $1.108M | $-0.000M | $-0.000M | $-1.420M | $-3.000M |
| LMP + BESS both | $4.906M | $1.631M | $-0.000M | $-0.000M | $-2.829M | $-6.000M |
| LMP + toll + BESS Houston | $2.836M | $7.111M | $-4.492M | $-4.800M | $-1.408M | $-3.000M |
| LMP + toll + BESS West | $2.313M | $7.922M | $-4.492M | $-4.800M | $-1.420M | $-3.000M |
| LMP + toll + BESS both | $5.464M | $7.895M | $-4.492M | $-4.800M | $-2.829M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.88 | Mean @ K=$3.88 | Δ vs LMP-only | MW @ K=$3.50 | Mean @ K=$3.50 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $76,122.27M ★ | +0.000 | n/a | $76,122.27M ★ | +0.000 | n/a | $76,122.27M | +0.000 | n/a | $76,122.27M | +0.000 |
| LMP + toll | 0 MW | $76,122.27M | +0.000 | 0 MW | $76,122.27M | +0.000 | 60 MW | $76,122.28M ★ | +0.006 | 100 MW | $76,122.51M ★ | +0.233 |
| LMP + BESS West | n/a | $76,121.27M | -1.008 | n/a | $76,121.27M | -1.008 | n/a | $76,121.27M | -1.008 | n/a | $76,121.27M | -1.008 |
| LMP + toll + BESS West | 0 MW | $76,121.27M | -1.008 | 0 MW | $76,121.27M | -1.008 | 60 MW | $76,121.27M | -1.002 | 100 MW | $76,121.50M | -0.775 |
| LMP + BESS Houston | n/a | $76,120.99M | -1.284 | n/a | $76,120.99M | -1.284 | n/a | $76,120.99M | -1.284 | n/a | $76,120.99M | -1.284 |
| LMP + toll + BESS Houston | 0 MW | $76,120.99M | -1.284 | 0 MW | $76,120.99M | -1.284 | 60 MW | $76,121.00M | -1.278 | 100 MW | $76,121.22M | -1.050 |
| LMP + BESS both | n/a | $76,119.98M | -2.292 | n/a | $76,119.98M | -2.292 | n/a | $76,119.98M | -2.292 | n/a | $76,119.98M | -2.292 |
| LMP + toll + BESS both | 0 MW | $76,119.98M | -2.292 | 0 MW | $76,119.98M | -2.292 | 60 MW | $76,119.99M | -2.286 | 100 MW | $76,120.22M | -2.058 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.469 | +0.334 | -2.884 | -1.975 |
| LMP + BESS Houston | -1.284 | +0.081 | -1.380 | -1.141 |
| LMP + BESS West | -1.008 | +0.098 | -1.170 | -0.854 |
| LMP + BESS both | -2.292 | +0.162 | -2.515 | -1.965 |
| LMP + toll + BESS Houston | -3.753 | +0.410 | -4.240 | -3.145 |
| LMP + toll + BESS West | -3.477 | +0.395 | -3.975 | -2.810 |
| LMP + toll + BESS both | -4.761 | +0.472 | -5.334 | -3.951 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $76,122.27M | $1.67M | $0.00M | $76,122.27M |
| 20 MW | $76,122.74M | $1.62M | $0.96M | $76,121.78M |
| 40 MW | $76,123.21M | $1.57M | $1.92M | $76,121.29M |
| 60 MW | $76,123.68M | $1.53M | $2.88M | $76,120.80M |
| 80 MW | $76,124.14M | $1.48M | $3.84M | $76,120.30M |
| 100 MW | $76,124.60M | $1.44M | $4.80M | $76,119.80M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.331 | 100 MW | +2.331 |
| $1.00 | $0.60M | +1.731 | 100 MW | +1.731 |
| $2.00 | $1.20M | +1.131 | 100 MW | +1.131 |
| $2.50 | $1.50M | +0.831 | 100 MW | +0.831 |
| $3.00 | $1.80M | +0.531 | 100 MW | +0.531 |
| $3.50 | $2.10M | +0.231 | 100 MW | +0.231 |
| $4.00 | $2.40M | -0.069 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.269 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.469 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.869 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,119.55M | -2.728 | 58,793 | $3.536M | 1.8% |
| intermediate (1500) | 1,500 | $76,119.78M | -2.492 | 72,869 | $4.371M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,119.80M | -2.469 | 74,894 | $4.490M | 0.7% |
| uncapped (None) | uncapped | $76,119.80M | -2.469 | 74,925 | $4.492M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.560M | $0.077M | $1.463M | $1.684M | $1.560M | $3.000M | $-1.440M |
| WEST | 4 | D | $1.824M | $0.097M | $1.654M | $1.969M | $1.824M | $3.000M | $-1.176M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.516M | $0.485M | $0.562M | $0.516M | $-2.484M |
| HOUSTON | 2 | D | $0.939M | $0.878M | $1.016M | $0.939M | $-2.061M |
| HOUSTON | 4 | D | $1.560M | $1.463M | $1.684M | $1.560M | $-1.440M |
| HOUSTON | 8 | D | $2.267M | $2.125M | $2.455M | $2.267M | $-0.733M |
| WEST | 1 | D | $0.594M | $0.539M | $0.647M | $0.594M | $-2.406M |
| WEST | 2 | D | $1.088M | $0.988M | $1.182M | $1.088M | $-1.912M |
| WEST | 4 | D | $1.824M | $1.654M | $1.969M | $1.824M | $-1.176M |
| WEST | 8 | D | $2.634M | $2.377M | $2.844M | $2.634M | $-0.366M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.961M | $1.560M | $1.560M | $-1.440M | -0.521 |
| WEST | $-1.961M | $1.824M | $1.824M | $-1.176M | -0.785 |
