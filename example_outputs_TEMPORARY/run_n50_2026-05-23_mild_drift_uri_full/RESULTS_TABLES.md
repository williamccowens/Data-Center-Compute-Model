# Results tables — `run_n50_2026-05-23_mild_drift_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,092.56M | $24.73M | $148,019.77M | $148,102.40M |
| 90d | $144,742.07M | $24.73M | $144,669.27M | $144,751.91M |
| 85d | $141,545.23M | $24.73M | $141,472.44M | $141,555.07M |
| 75d | $135,564.75M | $24.73M | $135,491.96M | $135,574.59M |
| 74d | $134,880.37M | $24.73M | $134,807.58M | $134,890.21M |
| 63d | $126,269.73M | $24.73M | $126,196.93M | $126,279.57M |
| 60d | $123,558.68M | $24.73M | $123,485.88M | $123,568.52M |
| 45d | $106,456.83M | $24.73M | $106,384.04M | $106,466.67M |
| 30d | $76,110.14M | $24.73M | $76,037.34M | $76,119.98M |
| 25d | $59,072.41M | $24.73M | $58,999.62M | $59,082.25M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $76,111.77M | $26.97M | $76,032.25M | $76,122.48M | +2.330 |
| LMP + toll + BESS West | $76,111.09M | $25.86M | $76,034.97M | $76,121.35M | +1.649 |
| LMP + toll + BESS Houston | $76,110.82M | $25.85M | $76,034.62M | $76,121.10M | +1.379 |
| LMP + toll + BESS both | $76,110.14M | $24.73M | $76,037.34M | $76,119.98M | +0.698 |
| LMP only | $76,109.44M | $41.64M | $75,984.54M | $76,125.32M | +0.000 |
| LMP + BESS West | $76,108.76M | $40.52M | $75,987.17M | $76,124.14M | -0.681 |
| LMP + BESS Houston | $76,108.49M | $40.52M | $75,986.67M | $76,123.91M | -0.951 |
| LMP + BESS both | $76,107.81M | $39.40M | $75,989.26M | $76,122.72M | -1.633 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.540M | $-6.409M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $3.050M | $1.278M | $-0.000M | $-0.000M | $-2.279M | $-3.000M |
| LMP + BESS West | $3.113M | $1.458M | $-0.000M | $-0.000M | $-2.252M | $-3.000M |
| LMP + BESS both | $6.840M | $2.059M | $-0.000M | $-0.000M | $-4.531M | $-6.000M |
| LMP + toll + BESS Houston | $4.048M | $13.819M | $-6.409M | $-4.800M | $-2.279M | $-3.000M |
| LMP + toll + BESS West | $3.175M | $14.936M | $-6.409M | $-4.800M | $-2.252M | $-3.000M |
| LMP + toll + BESS both | $7.695M | $14.743M | $-6.409M | $-4.800M | $-4.531M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.88 | Mean @ K=$11.88 | Δ vs LMP-only | MW @ K=$10.70 | Mean @ K=$10.70 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $76,109.44M ★ | +0.006 | 100 MW | $76,110.15M ★ | +0.713 | 100 MW | $76,111.77M ★ | +2.330 | 100 MW | $76,113.57M ★ | +4.130 |
| LMP only | n/a | $76,109.44M | +0.000 | n/a | $76,109.44M | +0.000 | n/a | $76,109.44M | +0.000 | n/a | $76,109.44M | +0.000 |
| LMP + toll + BESS West | 60 MW | $76,108.76M | -0.676 | 100 MW | $76,109.47M | +0.032 | 100 MW | $76,111.09M | +1.649 | 100 MW | $76,112.89M | +3.449 |
| LMP + BESS West | n/a | $76,108.76M | -0.681 | n/a | $76,108.76M | -0.681 | n/a | $76,108.76M | -0.681 | n/a | $76,108.76M | -0.681 |
| LMP + toll + BESS Houston | 60 MW | $76,108.49M | -0.946 | 100 MW | $76,109.20M | -0.239 | 100 MW | $76,110.82M | +1.379 | 100 MW | $76,112.62M | +3.179 |
| LMP + BESS Houston | n/a | $76,108.49M | -0.951 | n/a | $76,108.49M | -0.951 | n/a | $76,108.49M | -0.951 | n/a | $76,108.49M | -0.951 |
| LMP + toll + BESS both | 60 MW | $76,107.81M | -1.627 | 100 MW | $76,108.52M | -0.920 | 100 MW | $76,110.14M | +0.698 | 100 MW | $76,111.94M | +2.498 |
| LMP + BESS both | n/a | $76,107.81M | -1.633 | n/a | $76,107.81M | -1.633 | n/a | $76,107.81M | -1.633 | n/a | $76,107.81M | -1.633 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.330 | +14.689 | -2.958 | +45.745 |
| LMP + BESS Houston | -0.951 | +1.132 | -1.411 | +2.441 |
| LMP + BESS West | -0.681 | +1.119 | -1.213 | +2.655 |
| LMP + BESS both | -1.633 | +2.247 | -2.597 | +4.995 |
| LMP + toll + BESS Houston | +1.379 | +15.811 | -4.355 | +48.248 |
| LMP + toll + BESS West | +1.649 | +15.803 | -4.096 | +48.424 |
| LMP + toll + BESS both | +0.698 | +16.926 | -5.494 | +50.926 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $76,109.44M | $41.64M | $0.00M | $76,109.44M |
| 20 MW | $76,110.87M | $38.71M | $0.96M | $76,109.91M |
| 40 MW | $76,112.29M | $35.77M | $1.92M | $76,110.37M |
| 60 MW | $76,113.72M | $32.84M | $2.88M | $76,110.84M |
| 80 MW | $76,115.15M | $29.91M | $3.84M | $76,111.31M |
| 100 MW ★ | $76,116.57M | $26.97M | $4.80M | $76,111.77M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.130 | 100 MW | +7.130 |
| $1.00 | $0.60M | +6.530 | 100 MW | +6.530 |
| $2.00 | $1.20M | +5.930 | 100 MW | +5.930 |
| $2.50 | $1.50M | +5.630 | 100 MW | +5.630 |
| $3.00 | $1.80M | +5.330 | 100 MW | +5.330 |
| $3.50 | $2.10M | +5.030 | 100 MW | +5.030 |
| $4.00 | $2.40M | +4.730 | 100 MW | +4.730 |
| $6.00 | $3.60M | +3.530 | 100 MW | +3.530 |
| $8.00 | $4.80M | +2.330 | 100 MW | +2.330 |
| $12.00 | $7.20M | -0.070 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,108.80M | -0.642 | 58,271 | $4.113M | 1.8% |
| intermediate (1500) | 1,500 | $76,110.61M | +1.176 | 72,275 | $5.583M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,111.67M | +2.228 | 74,491 | $6.320M | 0.7% |
| uncapped (None) | uncapped | $76,111.77M | +2.330 | 74,559 | $6.409M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.878M | $1.077M | $1.439M | $4.951M | $1.878M | $3.000M | $-1.122M |
| WEST | 4 | D | $2.136M | $1.072M | $1.615M | $5.259M | $2.136M | $3.000M | $-0.864M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.605M | $0.478M | $1.521M | $0.605M | $-2.395M |
| HOUSTON | 2 | D | $1.111M | $0.867M | $2.839M | $1.111M | $-1.889M |
| HOUSTON | 4 | D | $1.878M | $1.439M | $4.951M | $1.878M | $-1.122M |
| HOUSTON | 8 | D | $2.770M | $2.089M | $7.499M | $2.770M | $-0.230M |
| WEST | 1 | D | $0.683M | $0.526M | $1.598M | $0.683M | $-2.317M |
| WEST | 2 | D | $1.257M | $0.965M | $3.006M | $1.257M | $-1.743M |
| WEST | 4 | D | $2.136M | $1.615M | $5.259M | $2.136M | $-0.864M |
| WEST | 8 | D | $3.132M | $2.320M | $7.938M | $3.132M | $0.132M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.846M | $1.878M | $1.878M | $-1.122M | -0.723 |
| WEST | $-1.846M | $2.136M | $2.136M | $-0.864M | -0.981 |
