# Results tables — `run_n50_2026-05-24_baseline_moderate`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,370.66M | $3.83M | $36,362.37M | $36,373.78M |
| 85d | $35,585.19M | $3.83M | $35,576.90M | $35,588.31M |
| 75d | $34,140.91M | $3.83M | $34,132.62M | $34,144.03M |
| 74d | $33,974.59M | $3.83M | $33,966.30M | $33,977.71M |
| 63d | $31,871.91M | $3.83M | $31,863.62M | $31,875.03M |
| 60d | $31,207.63M | $3.83M | $31,199.34M | $31,210.74M |
| 45d | $27,065.47M | $3.83M | $27,057.18M | $27,068.59M |
| 30d | $19,745.60M | $3.83M | $19,737.31M | $19,748.72M |
| 25d | $15,644.11M | $3.83M | $15,635.82M | $15,647.22M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,749.00M | $7.38M | $19,732.49M | $19,754.19M | +0.000 |
| LMP + BESS West | $19,748.07M | $7.03M | $19,732.28M | $19,752.99M | -0.927 |
| LMP + BESS Houston | $19,747.80M | $7.04M | $19,732.09M | $19,752.75M | -1.199 |
| LMP + toll | $19,747.73M | $4.51M | $19,737.93M | $19,751.27M | -1.272 |
| LMP + BESS both | $19,746.87M | $6.69M | $19,731.87M | $19,751.54M | -2.126 |
| LMP + toll + BESS West | $19,746.80M | $4.16M | $19,737.72M | $19,750.11M | -2.199 |
| LMP + toll + BESS Houston | $19,746.53M | $4.17M | $19,737.53M | $19,749.87M | -2.471 |
| LMP + toll + BESS both | $19,745.60M | $3.83M | $19,737.31M | $19,748.72M | -3.398 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $8.106M | $-4.578M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.333M | $1.024M | $-0.000M | $-0.000M | $-1.556M | $-3.000M |
| LMP + BESS West | $2.491M | $1.125M | $-0.000M | $-0.000M | $-1.543M | $-3.000M |
| LMP + BESS both | $5.289M | $1.683M | $-0.000M | $-0.000M | $-3.098M | $-6.000M |
| LMP + toll + BESS Houston | $3.078M | $8.385M | $-4.578M | $-4.800M | $-1.556M | $-3.000M |
| LMP + toll + BESS West | $2.504M | $9.218M | $-4.578M | $-4.800M | $-1.543M | $-3.000M |
| LMP + toll + BESS both | $5.873M | $9.206M | $-4.578M | $-4.800M | $-3.098M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.87 | Mean @ K=$5.87 | Δ vs LMP-only | MW @ K=$5.29 | Mean @ K=$5.29 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,749.00M ★ | +0.000 | n/a | $19,749.00M | +0.000 | n/a | $19,749.00M | +0.000 | n/a | $19,749.00M | +0.000 |
| LMP + toll | 0 MW | $19,749.00M | +0.000 | 60 MW | $19,749.01M ★ | +0.010 | 100 MW | $19,749.35M ★ | +0.353 | 100 MW | $19,749.53M ★ | +0.528 |
| LMP + BESS West | n/a | $19,748.07M | -0.927 | n/a | $19,748.07M | -0.927 | n/a | $19,748.07M | -0.927 | n/a | $19,748.07M | -0.927 |
| LMP + toll + BESS West | 0 MW | $19,748.07M | -0.927 | 60 MW | $19,748.08M | -0.917 | 100 MW | $19,748.42M | -0.574 | 100 MW | $19,748.60M | -0.399 |
| LMP + BESS Houston | n/a | $19,747.80M | -1.199 | n/a | $19,747.80M | -1.199 | n/a | $19,747.80M | -1.199 | n/a | $19,747.80M | -1.199 |
| LMP + toll + BESS Houston | 0 MW | $19,747.80M | -1.199 | 60 MW | $19,747.81M | -1.189 | 100 MW | $19,748.15M | -0.846 | 100 MW | $19,748.33M | -0.671 |
| LMP + BESS both | n/a | $19,746.87M | -2.126 | n/a | $19,746.87M | -2.126 | n/a | $19,746.87M | -2.126 | n/a | $19,746.87M | -2.126 |
| LMP + toll + BESS both | 0 MW | $19,746.87M | -2.126 | 60 MW | $19,746.88M | -2.116 | 100 MW | $19,747.22M | -1.773 | 100 MW | $19,747.40M | -1.598 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.272 | +2.955 | -3.024 | +5.437 |
| LMP + BESS Houston | -1.199 | +0.350 | -1.433 | -0.401 |
| LMP + BESS West | -0.927 | +0.357 | -1.238 | -0.157 |
| LMP + BESS both | -2.126 | +0.702 | -2.646 | -0.585 |
| LMP + toll + BESS Houston | -2.471 | +3.299 | -4.436 | +5.030 |
| LMP + toll + BESS West | -2.199 | +3.301 | -4.184 | +5.173 |
| LMP + toll + BESS both | -3.398 | +3.646 | -5.606 | +4.771 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,749.00M | $7.38M | $0.00M | $19,749.00M |
| 20 MW | $19,749.71M | $6.80M | $0.96M | $19,748.75M |
| 40 MW | $19,750.42M | $6.22M | $1.92M | $19,748.50M |
| 60 MW | $19,751.12M | $5.65M | $2.88M | $19,748.24M |
| 80 MW | $19,751.83M | $5.07M | $3.84M | $19,747.99M |
| 100 MW | $19,752.53M | $4.51M | $4.80M | $19,747.73M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +3.528 | 100 MW | +3.528 |
| $1.00 | $0.60M | +2.928 | 100 MW | +2.928 |
| $2.00 | $1.20M | +2.328 | 100 MW | +2.328 |
| $2.50 | $1.50M | +2.028 | 100 MW | +2.028 |
| $3.00 | $1.80M | +1.728 | 100 MW | +1.728 |
| $3.50 | $2.10M | +1.428 | 100 MW | +1.428 |
| $4.00 | $2.40M | +1.128 | 100 MW | +1.128 |
| $6.00 | $3.60M | -0.072 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.272 | 0 MW | +0.000 |
| $12.00 | $7.20M | -3.672 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,746.78M | -2.222 | 58,114 | $3.463M | 1.8% |
| intermediate (1500) | 1,500 | $19,747.43M | -1.564 | 72,214 | $4.353M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,747.70M | -1.294 | 74,598 | $4.563M | 0.7% |
| uncapped (None) | uncapped | $19,747.73M | -1.272 | 74,694 | $4.578M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.611M | $0.267M | $1.418M | $2.255M | $1.611M | $3.000M | $-1.389M |
| WEST | 4 | D | $1.867M | $0.277M | $1.591M | $2.498M | $1.867M | $3.000M | $-1.133M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.529M | $0.471M | $0.706M | $0.529M | $-2.471M |
| HOUSTON | 2 | D | $0.965M | $0.854M | $1.312M | $0.965M | $-2.035M |
| HOUSTON | 4 | D | $1.611M | $1.418M | $2.255M | $1.611M | $-1.389M |
| HOUSTON | 8 | D | $2.356M | $2.058M | $3.331M | $2.356M | $-0.644M |
| WEST | 1 | D | $0.605M | $0.519M | $0.788M | $0.605M | $-2.395M |
| WEST | 2 | D | $1.110M | $0.950M | $1.462M | $1.110M | $-1.890M |
| WEST | 4 | D | $1.867M | $1.591M | $2.498M | $1.867M | $-1.133M |
| WEST | 8 | D | $2.712M | $2.285M | $3.655M | $2.712M | $-0.288M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.905M | $1.611M | $1.611M | $-1.389M | -0.516 |
| WEST | $-1.905M | $1.867M | $1.867M | $-1.133M | -0.771 |
