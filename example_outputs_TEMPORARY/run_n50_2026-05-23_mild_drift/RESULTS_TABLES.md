# Results tables — `run_n50_2026-05-23_mild_drift`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,100.79M | $1.27M | $148,098.72M | $148,102.40M |
| 90d | $144,750.29M | $1.27M | $144,748.23M | $144,751.91M |
| 85d | $141,553.46M | $1.27M | $141,551.40M | $141,555.07M |
| 75d | $135,572.98M | $1.27M | $135,570.91M | $135,574.59M |
| 74d | $134,888.59M | $1.27M | $134,886.53M | $134,890.21M |
| 63d | $126,277.95M | $1.27M | $126,275.89M | $126,279.57M |
| 60d | $123,566.90M | $1.27M | $123,564.84M | $123,568.52M |
| 45d | $106,465.06M | $1.27M | $106,463.00M | $106,466.67M |
| 30d | $76,118.36M | $1.27M | $76,116.30M | $76,119.98M |
| 25d | $59,080.64M | $1.27M | $59,078.57M | $59,082.25M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $76,123.30M | $1.63M | $76,120.68M | $76,125.32M | +0.000 |
| LMP + BESS West | $76,122.24M | $1.55M | $76,119.76M | $76,124.14M | -1.054 |
| LMP + BESS Houston | $76,121.97M | $1.57M | $76,119.46M | $76,123.91M | -1.325 |
| LMP + BESS both | $76,120.92M | $1.49M | $76,118.54M | $76,122.72M | -2.379 |
| LMP + toll | $76,120.74M | $1.40M | $76,118.44M | $76,122.48M | -2.558 |
| LMP + toll + BESS West | $76,119.69M | $1.32M | $76,117.52M | $76,121.35M | -3.612 |
| LMP + toll + BESS Houston | $76,119.42M | $1.35M | $76,117.22M | $76,121.10M | -3.883 |
| LMP + toll + BESS both | $76,118.36M | $1.27M | $76,116.30M | $76,119.98M | -4.937 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.587M | $-4.345M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.090M | $0.958M | $-0.000M | $-0.000M | $-1.373M | $-3.000M |
| LMP + BESS West | $2.248M | $1.066M | $-0.000M | $-0.000M | $-1.369M | $-3.000M |
| LMP + BESS both | $4.752M | $1.611M | $-0.000M | $-0.000M | $-2.742M | $-6.000M |
| LMP + toll + BESS Houston | $2.770M | $6.866M | $-4.345M | $-4.800M | $-1.373M | $-3.000M |
| LMP + toll + BESS West | $2.258M | $7.644M | $-4.345M | $-4.800M | $-1.369M | $-3.000M |
| LMP + toll + BESS both | $5.324M | $7.627M | $-4.345M | $-4.800M | $-2.742M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.73 | Mean @ K=$3.73 | Δ vs LMP-only | MW @ K=$3.36 | Mean @ K=$3.36 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $76,123.30M ★ | +0.000 | n/a | $76,123.30M ★ | +0.000 | n/a | $76,123.30M | +0.000 | n/a | $76,123.30M | +0.000 |
| LMP + toll | 0 MW | $76,123.30M | +0.000 | 0 MW | $76,123.30M | +0.000 | 60 MW | $76,123.30M ★ | +0.006 | 100 MW | $76,123.52M ★ | +0.224 |
| LMP + BESS West | n/a | $76,122.24M | -1.054 | n/a | $76,122.24M | -1.054 | n/a | $76,122.24M | -1.054 | n/a | $76,122.24M | -1.054 |
| LMP + toll + BESS West | 0 MW | $76,122.24M | -1.054 | 0 MW | $76,122.24M | -1.054 | 60 MW | $76,122.25M | -1.048 | 100 MW | $76,122.47M | -0.830 |
| LMP + BESS Houston | n/a | $76,121.97M | -1.325 | n/a | $76,121.97M | -1.325 | n/a | $76,121.97M | -1.325 | n/a | $76,121.97M | -1.325 |
| LMP + toll + BESS Houston | 0 MW | $76,121.97M | -1.325 | 0 MW | $76,121.97M | -1.325 | 60 MW | $76,121.98M | -1.319 | 100 MW | $76,122.20M | -1.100 |
| LMP + BESS both | n/a | $76,120.92M | -2.379 | n/a | $76,120.92M | -2.379 | n/a | $76,120.92M | -2.379 | n/a | $76,120.92M | -2.379 |
| LMP + toll + BESS both | 0 MW | $76,120.92M | -2.379 | 0 MW | $76,120.92M | -2.379 | 60 MW | $76,120.93M | -2.373 | 100 MW | $76,121.14M | -2.155 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.558 | +0.324 | -2.958 | -2.080 |
| LMP + BESS Houston | -1.325 | +0.079 | -1.419 | -1.185 |
| LMP + BESS West | -1.054 | +0.095 | -1.213 | -0.904 |
| LMP + BESS both | -2.379 | +0.158 | -2.597 | -2.061 |
| LMP + toll + BESS Houston | -3.883 | +0.398 | -4.355 | -3.294 |
| LMP + toll + BESS West | -3.612 | +0.384 | -4.096 | -2.965 |
| LMP + toll + BESS both | -4.937 | +0.459 | -5.494 | -4.151 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $76,123.30M | $1.63M | $0.00M | $76,123.30M |
| 20 MW | $76,123.75M | $1.58M | $0.96M | $76,122.79M |
| 40 MW | $76,124.20M | $1.54M | $1.92M | $76,122.28M |
| 60 MW | $76,124.65M | $1.49M | $2.88M | $76,121.77M |
| 80 MW | $76,125.10M | $1.45M | $3.84M | $76,121.26M |
| 100 MW | $76,125.54M | $1.40M | $4.80M | $76,120.74M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.242 | 100 MW | +2.242 |
| $1.00 | $0.60M | +1.642 | 100 MW | +1.642 |
| $2.00 | $1.20M | +1.042 | 100 MW | +1.042 |
| $2.50 | $1.50M | +0.742 | 100 MW | +0.742 |
| $3.00 | $1.80M | +0.442 | 100 MW | +0.442 |
| $3.50 | $2.10M | +0.142 | 100 MW | +0.142 |
| $4.00 | $2.40M | -0.158 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.358 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.558 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.958 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,120.49M | -2.804 | 58,069 | $3.432M | 1.8% |
| intermediate (1500) | 1,500 | $76,120.72M | -2.579 | 71,783 | $4.232M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,120.74M | -2.558 | 73,716 | $4.343M | 0.7% |
| uncapped (None) | uncapped | $76,120.74M | -2.558 | 73,747 | $4.345M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.522M | $0.075M | $1.428M | $1.643M | $1.522M | $3.000M | $-1.478M |
| WEST | 4 | D | $1.780M | $0.094M | $1.615M | $1.922M | $1.780M | $3.000M | $-1.220M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.503M | $0.473M | $0.548M | $0.503M | $-2.497M |
| HOUSTON | 2 | D | $0.917M | $0.857M | $0.992M | $0.917M | $-2.083M |
| HOUSTON | 4 | D | $1.522M | $1.428M | $1.643M | $1.522M | $-1.478M |
| HOUSTON | 8 | D | $2.213M | $2.074M | $2.396M | $2.213M | $-0.787M |
| WEST | 1 | D | $0.580M | $0.526M | $0.631M | $0.580M | $-2.420M |
| WEST | 2 | D | $1.062M | $0.965M | $1.153M | $1.062M | $-1.938M |
| WEST | 4 | D | $1.780M | $1.615M | $1.922M | $1.780M | $-1.220M |
| WEST | 8 | D | $2.571M | $2.320M | $2.776M | $2.571M | $-0.429M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.995M | $1.522M | $1.522M | $-1.478M | -0.517 |
| WEST | $-1.995M | $1.780M | $1.780M | $-1.220M | -0.775 |
