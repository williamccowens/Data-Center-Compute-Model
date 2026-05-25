# Results tables — `run_n50_2026-05-24_ai_plus_brent`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,370.84M | $1.29M | $36,368.72M | $36,372.47M |
| 85d | $35,585.37M | $1.29M | $35,583.25M | $35,586.99M |
| 75d | $34,141.09M | $1.29M | $34,138.97M | $34,142.71M |
| 74d | $33,974.77M | $1.29M | $33,972.65M | $33,976.40M |
| 63d | $31,872.09M | $1.29M | $31,869.97M | $31,873.71M |
| 60d | $31,207.81M | $1.29M | $31,205.69M | $31,209.43M |
| 45d | $27,065.65M | $1.29M | $27,063.53M | $27,067.27M |
| 30d | $19,745.78M | $1.29M | $19,743.66M | $19,747.40M |
| 25d | $15,644.29M | $1.29M | $15,642.17M | $15,645.91M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,750.57M | $1.66M | $19,747.87M | $19,752.64M | +0.000 |
| LMP + BESS West | $19,749.56M | $1.58M | $19,746.99M | $19,751.50M | -1.008 |
| LMP + BESS Houston | $19,749.28M | $1.60M | $19,746.69M | $19,751.26M | -1.284 |
| LMP + BESS both | $19,748.28M | $1.51M | $19,745.82M | $19,750.12M | -2.292 |
| LMP + toll | $19,748.07M | $1.43M | $19,745.71M | $19,749.82M | -2.499 |
| LMP + toll + BESS West | $19,747.06M | $1.35M | $19,744.84M | $19,748.74M | -3.507 |
| LMP + toll + BESS Houston | $19,746.79M | $1.37M | $19,744.53M | $19,748.49M | -3.783 |
| LMP + toll + BESS both | $19,745.78M | $1.29M | $19,743.66M | $19,747.40M | -4.791 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.761M | $-4.461M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.156M | $0.969M | $-0.000M | $-0.000M | $-1.408M | $-3.000M |
| LMP + BESS West | $2.345M | $1.068M | $-0.000M | $-0.000M | $-1.420M | $-3.000M |
| LMP + BESS both | $4.901M | $1.636M | $-0.000M | $-0.000M | $-2.829M | $-6.000M |
| LMP + toll + BESS Houston | $2.843M | $7.043M | $-4.461M | $-4.800M | $-1.408M | $-3.000M |
| LMP + toll + BESS West | $2.341M | $7.833M | $-4.461M | $-4.800M | $-1.420M | $-3.000M |
| LMP + toll + BESS both | $5.480M | $7.819M | $-4.461M | $-4.800M | $-2.829M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.83 | Mean @ K=$3.83 | Δ vs LMP-only | MW @ K=$3.45 | Mean @ K=$3.45 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,750.57M ★ | +0.000 | n/a | $19,750.57M ★ | +0.000 | n/a | $19,750.57M | +0.000 | n/a | $19,750.57M | +0.000 |
| LMP + toll | 0 MW | $19,750.57M | +0.000 | 0 MW | $19,750.57M | +0.000 | 60 MW | $19,750.58M ★ | +0.007 | 100 MW | $19,750.80M ★ | +0.230 |
| LMP + BESS West | n/a | $19,749.56M | -1.008 | n/a | $19,749.56M | -1.008 | n/a | $19,749.56M | -1.008 | n/a | $19,749.56M | -1.008 |
| LMP + toll + BESS West | 0 MW | $19,749.56M | -1.008 | 0 MW | $19,749.56M | -1.008 | 60 MW | $19,749.57M | -1.001 | 100 MW | $19,749.79M | -0.778 |
| LMP + BESS Houston | n/a | $19,749.28M | -1.284 | n/a | $19,749.28M | -1.284 | n/a | $19,749.28M | -1.284 | n/a | $19,749.28M | -1.284 |
| LMP + toll + BESS Houston | 0 MW | $19,749.28M | -1.284 | 0 MW | $19,749.28M | -1.284 | 60 MW | $19,749.29M | -1.277 | 100 MW | $19,749.52M | -1.053 |
| LMP + BESS both | n/a | $19,748.28M | -2.292 | n/a | $19,748.28M | -2.292 | n/a | $19,748.28M | -2.292 | n/a | $19,748.28M | -2.292 |
| LMP + toll + BESS both | 0 MW | $19,748.28M | -2.292 | 0 MW | $19,748.28M | -2.292 | 60 MW | $19,748.28M | -2.284 | 100 MW | $19,748.51M | -2.061 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.499 | +0.333 | -2.923 | -2.020 |
| LMP + BESS Houston | -1.284 | +0.081 | -1.380 | -1.141 |
| LMP + BESS West | -1.008 | +0.098 | -1.170 | -0.854 |
| LMP + BESS both | -2.292 | +0.162 | -2.515 | -1.965 |
| LMP + toll + BESS Houston | -3.783 | +0.409 | -4.271 | -3.188 |
| LMP + toll + BESS West | -3.507 | +0.395 | -4.011 | -2.836 |
| LMP + toll + BESS both | -4.791 | +0.472 | -5.370 | -3.977 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,750.57M | $1.66M | $0.00M | $19,750.57M |
| 20 MW | $19,751.03M | $1.61M | $0.96M | $19,750.07M |
| 40 MW | $19,751.49M | $1.56M | $1.92M | $19,749.57M |
| 60 MW | $19,751.95M | $1.52M | $2.88M | $19,749.07M |
| 80 MW | $19,752.41M | $1.47M | $3.84M | $19,748.57M |
| 100 MW | $19,752.87M | $1.43M | $4.80M | $19,748.07M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.301 | 100 MW | +2.301 |
| $1.00 | $0.60M | +1.701 | 100 MW | +1.701 |
| $2.00 | $1.20M | +1.101 | 100 MW | +1.101 |
| $2.50 | $1.50M | +0.801 | 100 MW | +0.801 |
| $3.00 | $1.80M | +0.501 | 100 MW | +0.501 |
| $3.50 | $2.10M | +0.201 | 100 MW | +0.201 |
| $4.00 | $2.40M | -0.099 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.299 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.499 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.899 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,747.82M | -2.753 | 58,423 | $3.513M | 1.8% |
| intermediate (1500) | 1,500 | $19,748.05M | -2.522 | 72,371 | $4.341M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,748.07M | -2.499 | 74,379 | $4.459M | 0.7% |
| uncapped (None) | uncapped | $19,748.07M | -2.499 | 74,411 | $4.461M |  |

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
| HOUSTON | $-1.964M | $1.560M | $1.560M | $-1.440M | -0.524 |
| WEST | $-1.964M | $1.824M | $1.824M | $-1.176M | -0.787 |
