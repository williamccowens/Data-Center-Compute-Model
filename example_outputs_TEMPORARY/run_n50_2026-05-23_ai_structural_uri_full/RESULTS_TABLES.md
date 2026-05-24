# Results tables — `run_n50_2026-05-23_ai_structural_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,092.77M | $24.73M | $148,019.97M | $148,102.60M |
| 90d | $144,742.28M | $24.73M | $144,669.47M | $144,752.11M |
| 85d | $141,545.44M | $24.73M | $141,472.64M | $141,555.27M |
| 75d | $135,564.96M | $24.73M | $135,492.16M | $135,574.79M |
| 74d | $134,880.58M | $24.73M | $134,807.78M | $134,890.41M |
| 63d | $126,269.94M | $24.73M | $126,197.13M | $126,279.77M |
| 60d | $123,558.88M | $24.73M | $123,486.08M | $123,568.72M |
| 45d | $106,457.04M | $24.73M | $106,384.24M | $106,466.87M |
| 30d | $76,110.35M | $24.73M | $76,037.54M | $76,120.18M |
| 25d | $59,072.62M | $24.73M | $58,999.82M | $59,082.45M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $76,112.00M | $26.97M | $76,032.46M | $76,122.69M | +2.352 |
| LMP + toll + BESS West | $76,111.30M | $25.86M | $76,035.17M | $76,121.56M | +1.662 |
| LMP + toll + BESS Houston | $76,111.04M | $25.85M | $76,034.83M | $76,121.31M | +1.393 |
| LMP + toll + BESS both | $76,110.35M | $24.73M | $76,037.54M | $76,120.18M | +0.702 |
| LMP only | $76,109.64M | $41.64M | $75,984.73M | $76,125.52M | +0.000 |
| LMP + BESS West | $76,108.95M | $40.53M | $75,987.36M | $76,124.33M | -0.690 |
| LMP + BESS Houston | $76,108.68M | $40.52M | $75,986.87M | $76,124.09M | -0.960 |
| LMP + BESS both | $76,107.99M | $39.40M | $75,989.44M | $76,122.90M | -1.650 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.578M | $-6.426M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $3.035M | $1.278M | $-0.000M | $-0.000M | $-2.272M | $-3.000M |
| LMP + BESS West | $3.166M | $1.386M | $-0.000M | $-0.000M | $-2.242M | $-3.000M |
| LMP + BESS both | $6.773M | $2.091M | $-0.000M | $-0.000M | $-4.514M | $-6.000M |
| LMP + toll + BESS Houston | $4.032M | $13.859M | $-6.426M | $-4.800M | $-2.272M | $-3.000M |
| LMP + toll + BESS West | $3.140M | $14.990M | $-6.426M | $-4.800M | $-2.242M | $-3.000M |
| LMP + toll + BESS both | $7.567M | $14.876M | $-6.426M | $-4.800M | $-4.514M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.92 | Mean @ K=$11.92 | Δ vs LMP-only | MW @ K=$10.73 | Mean @ K=$10.73 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $76,109.65M ★ | +0.005 | 100 MW | $76,110.36M ★ | +0.715 | 100 MW | $76,112.00M ★ | +2.352 | 100 MW | $76,113.80M ★ | +4.152 |
| LMP only | n/a | $76,109.64M | +0.000 | n/a | $76,109.64M | +0.000 | n/a | $76,109.64M | +0.000 | n/a | $76,109.64M | +0.000 |
| LMP + toll + BESS West | 60 MW | $76,108.96M | -0.685 | 100 MW | $76,109.67M | +0.025 | 100 MW | $76,111.30M | +1.662 | 100 MW | $76,113.10M | +3.462 |
| LMP + BESS West | n/a | $76,108.95M | -0.690 | n/a | $76,108.95M | -0.690 | n/a | $76,108.95M | -0.690 | n/a | $76,108.95M | -0.690 |
| LMP + toll + BESS Houston | 60 MW | $76,108.69M | -0.954 | 100 MW | $76,109.40M | -0.244 | 100 MW | $76,111.04M | +1.393 | 100 MW | $76,112.84M | +3.193 |
| LMP + BESS Houston | n/a | $76,108.68M | -0.960 | n/a | $76,108.68M | -0.960 | n/a | $76,108.68M | -0.960 | n/a | $76,108.68M | -0.960 |
| LMP + toll + BESS both | 60 MW | $76,108.00M | -1.645 | 100 MW | $76,108.71M | -0.935 | 100 MW | $76,110.35M | +0.702 | 100 MW | $76,112.15M | +2.502 |
| LMP + BESS both | n/a | $76,107.99M | -1.650 | n/a | $76,107.99M | -1.650 | n/a | $76,107.99M | -1.650 | n/a | $76,107.99M | -1.650 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.352 | +14.689 | -2.940 | +45.771 |
| LMP + BESS Houston | -0.960 | +1.132 | -1.419 | +2.433 |
| LMP + BESS West | -0.690 | +1.119 | -1.221 | +2.646 |
| LMP + BESS both | -1.650 | +2.247 | -2.614 | +4.978 |
| LMP + toll + BESS Houston | +1.393 | +15.811 | -4.342 | +48.266 |
| LMP + toll + BESS West | +1.662 | +15.804 | -4.083 | +48.440 |
| LMP + toll + BESS both | +0.702 | +16.926 | -5.489 | +50.935 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $76,109.64M | $41.64M | $0.00M | $76,109.64M |
| 20 MW | $76,111.08M | $38.71M | $0.96M | $76,110.12M |
| 40 MW | $76,112.51M | $35.77M | $1.92M | $76,110.59M |
| 60 MW | $76,113.94M | $32.84M | $2.88M | $76,111.06M |
| 80 MW | $76,115.37M | $29.91M | $3.84M | $76,111.53M |
| 100 MW ★ | $76,116.80M | $26.97M | $4.80M | $76,112.00M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.152 | 100 MW | +7.152 |
| $1.00 | $0.60M | +6.552 | 100 MW | +6.552 |
| $2.00 | $1.20M | +5.952 | 100 MW | +5.952 |
| $2.50 | $1.50M | +5.652 | 100 MW | +5.652 |
| $3.00 | $1.80M | +5.352 | 100 MW | +5.352 |
| $3.50 | $2.10M | +5.052 | 100 MW | +5.052 |
| $4.00 | $2.40M | +4.752 | 100 MW | +4.752 |
| $6.00 | $3.60M | +3.552 | 100 MW | +3.552 |
| $8.00 | $4.80M | +2.352 | 100 MW | +2.352 |
| $12.00 | $7.20M | -0.048 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,109.02M | -0.625 | 59,030 | $4.115M | 1.9% |
| intermediate (1500) | 1,500 | $76,110.84M | +1.197 | 73,405 | $5.597M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,111.89M | +2.250 | 75,697 | $6.337M | 0.8% |
| uncapped (None) | uncapped | $76,112.00M | +2.352 | 75,765 | $6.426M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.870M | $1.077M | $1.432M | $4.943M | $1.870M | $3.000M | $-1.130M |
| WEST | 4 | D | $2.127M | $1.072M | $1.607M | $5.251M | $2.127M | $3.000M | $-0.873M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.603M | $0.476M | $1.518M | $0.603M | $-2.397M |
| HOUSTON | 2 | D | $1.107M | $0.863M | $2.835M | $1.107M | $-1.893M |
| HOUSTON | 4 | D | $1.870M | $1.432M | $4.943M | $1.870M | $-1.130M |
| HOUSTON | 8 | D | $2.759M | $2.079M | $7.489M | $2.759M | $-0.241M |
| WEST | 1 | D | $0.680M | $0.524M | $1.595M | $0.680M | $-2.320M |
| WEST | 2 | D | $1.252M | $0.960M | $3.001M | $1.252M | $-1.748M |
| WEST | 4 | D | $2.127M | $1.607M | $5.251M | $2.127M | $-0.873M |
| WEST | 8 | D | $3.119M | $2.308M | $7.926M | $3.119M | $0.119M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.870M | $1.870M | $1.870M | $-1.130M | -0.741 |
| WEST | $-1.870M | $2.127M | $2.127M | $-0.873M | -0.998 |
