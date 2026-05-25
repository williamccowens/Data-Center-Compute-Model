# Results tables — `run_n50_2026-05-24_ai_structural_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,363.67M | $24.73M | $36,290.84M | $36,373.47M |
| 85d | $35,578.20M | $24.73M | $35,505.37M | $35,588.00M |
| 75d | $34,133.92M | $24.73M | $34,061.09M | $34,143.72M |
| 74d | $33,967.60M | $24.73M | $33,894.77M | $33,977.40M |
| 63d | $31,864.91M | $24.73M | $31,792.09M | $31,874.72M |
| 60d | $31,200.63M | $24.73M | $31,127.81M | $31,210.44M |
| 45d | $27,058.47M | $24.73M | $26,985.65M | $27,068.28M |
| 30d | $19,738.61M | $24.73M | $19,665.78M | $19,748.41M |
| 25d | $15,637.11M | $24.73M | $15,564.29M | $15,646.92M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $19,740.26M | $26.98M | $19,660.70M | $19,750.93M | +2.323 |
| LMP + toll + BESS West | $19,739.57M | $25.86M | $19,663.41M | $19,749.79M | +1.633 |
| LMP + toll + BESS Houston | $19,739.30M | $25.85M | $19,663.07M | $19,749.55M | +1.363 |
| LMP + toll + BESS both | $19,738.61M | $24.73M | $19,665.78M | $19,748.41M | +0.673 |
| LMP only | $19,737.93M | $41.64M | $19,612.99M | $19,753.80M | +0.000 |
| LMP + BESS West | $19,737.24M | $40.53M | $19,615.62M | $19,752.61M | -0.690 |
| LMP + BESS Houston | $19,736.97M | $40.52M | $19,615.16M | $19,752.38M | -0.960 |
| LMP + BESS both | $19,736.28M | $39.40M | $19,617.70M | $19,751.19M | -1.650 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.517M | $-6.394M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $3.002M | $1.310M | $-0.000M | $-0.000M | $-2.272M | $-3.000M |
| LMP + BESS West | $3.247M | $1.305M | $-0.000M | $-0.000M | $-2.242M | $-3.000M |
| LMP + BESS both | $6.779M | $2.085M | $-0.000M | $-0.000M | $-4.514M | $-6.000M |
| LMP + toll + BESS Houston | $4.038M | $13.791M | $-6.394M | $-4.800M | $-2.272M | $-3.000M |
| LMP + toll + BESS West | $3.169M | $14.899M | $-6.394M | $-4.800M | $-2.242M | $-3.000M |
| LMP + toll + BESS both | $7.574M | $14.807M | $-6.394M | $-4.800M | $-4.514M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.87 | Mean @ K=$11.87 | Δ vs LMP-only | MW @ K=$10.69 | Mean @ K=$10.69 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $19,737.94M ★ | +0.007 | 100 MW | $19,738.64M ★ | +0.712 | 100 MW | $19,740.26M ★ | +2.323 | 100 MW | $19,742.06M ★ | +4.123 |
| LMP only | n/a | $19,737.93M | +0.000 | n/a | $19,737.93M | +0.000 | n/a | $19,737.93M | +0.000 | n/a | $19,737.93M | +0.000 |
| LMP + toll + BESS West | 60 MW | $19,737.25M | -0.683 | 100 MW | $19,737.95M | +0.022 | 100 MW | $19,739.57M | +1.633 | 100 MW | $19,741.37M | +3.433 |
| LMP + BESS West | n/a | $19,737.24M | -0.690 | n/a | $19,737.24M | -0.690 | n/a | $19,737.24M | -0.690 | n/a | $19,737.24M | -0.690 |
| LMP + toll + BESS Houston | 60 MW | $19,736.98M | -0.953 | 100 MW | $19,737.69M | -0.248 | 100 MW | $19,739.30M | +1.363 | 100 MW | $19,741.10M | +3.163 |
| LMP + BESS Houston | n/a | $19,736.97M | -0.960 | n/a | $19,736.97M | -0.960 | n/a | $19,736.97M | -0.960 | n/a | $19,736.97M | -0.960 |
| LMP + toll + BESS both | 60 MW | $19,736.29M | -1.643 | 100 MW | $19,736.99M | -0.938 | 100 MW | $19,738.61M | +0.673 | 100 MW | $19,740.41M | +2.473 |
| LMP + BESS both | n/a | $19,736.28M | -1.650 | n/a | $19,736.28M | -1.650 | n/a | $19,736.28M | -1.650 | n/a | $19,736.28M | -1.650 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.323 | +14.689 | -2.977 | +45.736 |
| LMP + BESS Houston | -0.960 | +1.132 | -1.419 | +2.433 |
| LMP + BESS West | -0.690 | +1.119 | -1.221 | +2.646 |
| LMP + BESS both | -1.650 | +2.247 | -2.614 | +4.978 |
| LMP + toll + BESS Houston | +1.363 | +15.811 | -4.372 | +48.231 |
| LMP + toll + BESS West | +1.633 | +15.804 | -4.119 | +48.406 |
| LMP + toll + BESS both | +0.673 | +16.926 | -5.525 | +50.900 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $19,737.93M | $41.64M | $0.00M | $19,737.93M |
| 20 MW | $19,739.36M | $38.71M | $0.96M | $19,738.40M |
| 40 MW | $19,740.79M | $35.77M | $1.92M | $19,738.87M |
| 60 MW | $19,742.21M | $32.84M | $2.88M | $19,739.33M |
| 80 MW | $19,743.63M | $29.91M | $3.84M | $19,739.79M |
| 100 MW ★ | $19,745.06M | $26.98M | $4.80M | $19,740.26M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.123 | 100 MW | +7.123 |
| $1.00 | $0.60M | +6.523 | 100 MW | +6.523 |
| $2.00 | $1.20M | +5.923 | 100 MW | +5.923 |
| $2.50 | $1.50M | +5.623 | 100 MW | +5.623 |
| $3.00 | $1.80M | +5.323 | 100 MW | +5.323 |
| $3.50 | $2.10M | +5.023 | 100 MW | +5.023 |
| $4.00 | $2.40M | +4.723 | 100 MW | +4.723 |
| $6.00 | $3.60M | +3.523 | 100 MW | +3.523 |
| $8.00 | $4.80M | +2.323 | 100 MW | +2.323 |
| $12.00 | $7.20M | -0.077 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,737.28M | -0.650 | 58,648 | $4.093M | 1.8% |
| intermediate (1500) | 1,500 | $19,739.10M | +1.169 | 72,875 | $5.566M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,740.15M | +2.220 | 75,149 | $6.305M | 0.7% |
| uncapped (None) | uncapped | $19,740.26M | +2.323 | 75,217 | $6.394M |  |

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
| HOUSTON | $-1.868M | $1.870M | $1.870M | $-1.130M | -0.738 |
| WEST | $-1.868M | $2.127M | $2.127M | $-0.873M | -0.995 |
