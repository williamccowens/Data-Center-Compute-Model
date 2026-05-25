# Results tables — `run_n50_2026-05-24_mild_drift_mild`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,370.79M | $1.71M | $36,368.39M | $36,373.16M |
| 85d | $35,585.32M | $1.71M | $35,582.92M | $35,587.68M |
| 75d | $34,141.04M | $1.71M | $34,138.64M | $34,143.40M |
| 74d | $33,974.72M | $1.71M | $33,972.32M | $33,977.09M |
| 63d | $31,872.03M | $1.71M | $31,869.64M | $31,874.40M |
| 60d | $31,207.75M | $1.71M | $31,205.36M | $31,210.12M |
| 45d | $27,065.59M | $1.71M | $27,063.20M | $27,067.96M |
| 30d | $19,745.73M | $1.71M | $19,743.33M | $19,748.09M |
| 25d | $15,644.23M | $1.71M | $15,641.84M | $15,646.60M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,749.94M | $2.58M | $19,746.47M | $19,753.53M | +0.000 |
| LMP + BESS West | $19,748.93M | $2.48M | $19,745.58M | $19,752.35M | -1.006 |
| LMP + BESS Houston | $19,748.67M | $2.49M | $19,745.30M | $19,752.10M | -1.272 |
| LMP + toll | $19,748.00M | $1.90M | $19,745.42M | $19,750.61M | -1.937 |
| LMP + BESS both | $19,747.66M | $2.39M | $19,744.40M | $19,750.91M | -2.278 |
| LMP + toll + BESS West | $19,747.00M | $1.80M | $19,744.52M | $19,749.47M | -2.943 |
| LMP + toll + BESS Houston | $19,746.73M | $1.81M | $19,744.22M | $19,749.27M | -3.209 |
| LMP + toll + BESS both | $19,745.73M | $1.71M | $19,743.33M | $19,748.09M | -4.215 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $7.463M | $-4.599M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.239M | $0.978M | $-0.000M | $-0.000M | $-1.489M | $-3.000M |
| LMP + BESS West | $2.396M | $1.084M | $-0.000M | $-0.000M | $-1.486M | $-3.000M |
| LMP + BESS both | $5.025M | $1.672M | $-0.000M | $-0.000M | $-2.975M | $-6.000M |
| LMP + toll + BESS Houston | $2.941M | $7.738M | $-4.599M | $-4.800M | $-1.489M | $-3.000M |
| LMP + toll + BESS West | $2.387M | $8.556M | $-4.599M | $-4.800M | $-1.486M | $-3.000M |
| LMP + toll + BESS both | $5.633M | $8.526M | $-4.599M | $-4.800M | $-2.975M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$4.77 | Mean @ K=$4.77 | Δ vs LMP-only | MW @ K=$4.29 | Mean @ K=$4.29 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,749.94M ★ | +0.000 | n/a | $19,749.94M ★ | +0.000 | n/a | $19,749.94M | +0.000 | n/a | $19,749.94M | +0.000 |
| LMP + toll | 0 MW | $19,749.94M | +0.000 | 0 MW | $19,749.94M | +0.000 | 60 MW | $19,749.95M ★ | +0.008 | 100 MW | $19,750.23M ★ | +0.286 |
| LMP + BESS West | n/a | $19,748.93M | -1.006 | n/a | $19,748.93M | -1.006 | n/a | $19,748.93M | -1.006 | n/a | $19,748.93M | -1.006 |
| LMP + toll + BESS West | 0 MW | $19,748.93M | -1.006 | 0 MW | $19,748.93M | -1.006 | 60 MW | $19,748.94M | -0.998 | 100 MW | $19,749.22M | -0.720 |
| LMP + BESS Houston | n/a | $19,748.67M | -1.272 | n/a | $19,748.67M | -1.272 | n/a | $19,748.67M | -1.272 | n/a | $19,748.67M | -1.272 |
| LMP + toll + BESS Houston | 0 MW | $19,748.67M | -1.272 | 0 MW | $19,748.67M | -1.272 | 60 MW | $19,748.68M | -1.264 | 100 MW | $19,748.95M | -0.986 |
| LMP + BESS both | n/a | $19,747.66M | -2.278 | n/a | $19,747.66M | -2.278 | n/a | $19,747.66M | -2.278 | n/a | $19,747.66M | -2.278 |
| LMP + toll + BESS both | 0 MW | $19,747.66M | -2.278 | 0 MW | $19,747.66M | -2.278 | 60 MW | $19,747.67M | -2.270 | 100 MW | $19,747.95M | -1.992 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.937 | +0.784 | -2.919 | -0.761 |
| LMP + BESS Houston | -1.272 | +0.102 | -1.406 | -1.135 |
| LMP + BESS West | -1.006 | +0.118 | -1.200 | -0.863 |
| LMP + BESS both | -2.278 | +0.206 | -2.584 | -2.019 |
| LMP + toll + BESS Houston | -3.209 | +0.873 | -4.326 | -1.925 |
| LMP + toll + BESS West | -2.943 | +0.873 | -4.074 | -1.639 |
| LMP + toll + BESS both | -4.215 | +0.964 | -5.472 | -2.803 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,749.94M | $2.58M | $0.00M | $19,749.94M |
| 20 MW | $19,750.52M | $2.44M | $0.96M | $19,749.56M |
| 40 MW | $19,751.09M | $2.30M | $1.92M | $19,749.17M |
| 60 MW | $19,751.67M | $2.16M | $2.88M | $19,748.79M |
| 80 MW | $19,752.24M | $2.03M | $3.84M | $19,748.40M |
| 100 MW | $19,752.80M | $1.90M | $4.80M | $19,748.00M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.863 | 100 MW | +2.863 |
| $1.00 | $0.60M | +2.263 | 100 MW | +2.263 |
| $2.00 | $1.20M | +1.663 | 100 MW | +1.663 |
| $2.50 | $1.50M | +1.363 | 100 MW | +1.363 |
| $3.00 | $1.80M | +1.063 | 100 MW | +1.063 |
| $3.50 | $2.10M | +0.763 | 100 MW | +0.763 |
| $4.00 | $2.40M | +0.463 | 100 MW | +0.463 |
| $6.00 | $3.60M | -0.737 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.937 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.337 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,747.41M | -2.526 | 58,356 | $3.493M | 1.8% |
| intermediate (1500) | 1,500 | $19,747.85M | -2.090 | 72,955 | $4.388M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,747.99M | -1.949 | 75,717 | $4.586M | 0.8% |
| uncapped (None) | uncapped | $19,748.00M | -1.937 | 75,861 | $4.599M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.569M | $0.092M | $1.441M | $1.701M | $1.569M | $3.000M | $-1.431M |
| WEST | 4 | D | $1.821M | $0.114M | $1.634M | $1.978M | $1.821M | $3.000M | $-1.179M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.516M | $0.478M | $0.558M | $0.516M | $-2.484M |
| HOUSTON | 2 | D | $0.941M | $0.869M | $1.019M | $0.941M | $-2.059M |
| HOUSTON | 4 | D | $1.569M | $1.441M | $1.701M | $1.569M | $-1.431M |
| HOUSTON | 8 | D | $2.289M | $2.100M | $2.483M | $2.289M | $-0.711M |
| WEST | 1 | D | $0.591M | $0.534M | $0.639M | $0.591M | $-2.409M |
| WEST | 2 | D | $1.084M | $0.981M | $1.161M | $1.084M | $-1.916M |
| WEST | 4 | D | $1.821M | $1.634M | $1.978M | $1.821M | $-1.179M |
| WEST | 8 | D | $2.641M | $2.346M | $2.866M | $2.641M | $-0.359M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.975M | $1.569M | $1.569M | $-1.431M | -0.545 |
| WEST | $-1.975M | $1.821M | $1.821M | $-1.179M | -0.797 |
