# Results tables — `run_n50_2026-05-24_mild_drift_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,363.46M | $24.73M | $36,290.64M | $36,373.28M |
| 85d | $35,577.99M | $24.73M | $35,505.17M | $35,587.80M |
| 75d | $34,133.71M | $24.73M | $34,060.89M | $34,143.52M |
| 74d | $33,967.39M | $24.73M | $33,894.58M | $33,977.21M |
| 63d | $31,864.71M | $24.73M | $31,791.89M | $31,874.52M |
| 60d | $31,200.43M | $24.73M | $31,127.61M | $31,210.24M |
| 45d | $27,058.27M | $24.73M | $26,985.45M | $27,068.08M |
| 30d | $19,738.40M | $24.73M | $19,665.58M | $19,748.21M |
| 25d | $15,636.91M | $24.73M | $15,564.09M | $15,646.72M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $19,740.03M | $26.98M | $19,660.49M | $19,750.72M | +2.301 |
| LMP + toll + BESS West | $19,739.35M | $25.86M | $19,663.21M | $19,749.59M | +1.620 |
| LMP + toll + BESS Houston | $19,739.08M | $25.85M | $19,662.86M | $19,749.34M | +1.350 |
| LMP + toll + BESS both | $19,738.40M | $24.73M | $19,665.58M | $19,748.21M | +0.669 |
| LMP only | $19,737.73M | $41.64M | $19,612.80M | $19,753.61M | +0.000 |
| LMP + BESS West | $19,737.05M | $40.53M | $19,615.43M | $19,752.43M | -0.681 |
| LMP + BESS Houston | $19,736.78M | $40.52M | $19,614.96M | $19,752.19M | -0.951 |
| LMP + BESS both | $19,736.10M | $39.40M | $19,617.52M | $19,751.01M | -1.633 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.478M | $-6.376M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.970M | $1.357M | $-0.000M | $-0.000M | $-2.279M | $-3.000M |
| LMP + BESS West | $3.250M | $1.321M | $-0.000M | $-0.000M | $-2.252M | $-3.000M |
| LMP + BESS both | $6.697M | $2.201M | $-0.000M | $-0.000M | $-4.531M | $-6.000M |
| LMP + toll + BESS Houston | $4.048M | $13.757M | $-6.376M | $-4.800M | $-2.279M | $-3.000M |
| LMP + toll + BESS West | $3.083M | $14.966M | $-6.376M | $-4.800M | $-2.252M | $-3.000M |
| LMP + toll + BESS both | $7.562M | $14.814M | $-6.376M | $-4.800M | $-4.531M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.83 | Mean @ K=$11.83 | Δ vs LMP-only | MW @ K=$10.65 | Mean @ K=$10.65 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $19,737.74M ★ | +0.007 | 100 MW | $19,738.44M ★ | +0.710 | 100 MW | $19,740.03M ★ | +2.301 | 100 MW | $19,741.83M ★ | +4.101 |
| LMP only | n/a | $19,737.73M | +0.000 | n/a | $19,737.73M | +0.000 | n/a | $19,737.73M | +0.000 | n/a | $19,737.73M | +0.000 |
| LMP + toll + BESS West | 60 MW | $19,737.05M | -0.674 | 100 MW | $19,737.76M | +0.029 | 100 MW | $19,739.35M | +1.620 | 100 MW | $19,741.15M | +3.420 |
| LMP + BESS West | n/a | $19,737.05M | -0.681 | n/a | $19,737.05M | -0.681 | n/a | $19,737.05M | -0.681 | n/a | $19,737.05M | -0.681 |
| LMP + toll + BESS Houston | 60 MW | $19,736.78M | -0.944 | 100 MW | $19,737.49M | -0.241 | 100 MW | $19,739.08M | +1.350 | 100 MW | $19,740.88M | +3.150 |
| LMP + BESS Houston | n/a | $19,736.78M | -0.951 | n/a | $19,736.78M | -0.951 | n/a | $19,736.78M | -0.951 | n/a | $19,736.78M | -0.951 |
| LMP + toll + BESS both | 60 MW | $19,736.10M | -1.626 | 100 MW | $19,736.81M | -0.923 | 100 MW | $19,738.40M | +0.669 | 100 MW | $19,740.20M | +2.469 |
| LMP + BESS both | n/a | $19,736.10M | -1.633 | n/a | $19,736.10M | -1.633 | n/a | $19,736.10M | -1.633 | n/a | $19,736.10M | -1.633 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.301 | +14.689 | -2.997 | +45.710 |
| LMP + BESS Houston | -0.951 | +1.132 | -1.411 | +2.441 |
| LMP + BESS West | -0.681 | +1.119 | -1.213 | +2.655 |
| LMP + BESS both | -1.633 | +2.247 | -2.597 | +4.995 |
| LMP + toll + BESS Houston | +1.350 | +15.811 | -4.385 | +48.213 |
| LMP + toll + BESS West | +1.620 | +15.803 | -4.131 | +48.389 |
| LMP + toll + BESS both | +0.669 | +16.926 | -5.529 | +50.891 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $19,737.73M | $41.64M | $0.00M | $19,737.73M |
| 20 MW | $19,739.15M | $38.71M | $0.96M | $19,738.19M |
| 40 MW | $19,740.57M | $35.77M | $1.92M | $19,738.65M |
| 60 MW | $19,741.99M | $32.84M | $2.88M | $19,739.11M |
| 80 MW | $19,743.41M | $29.91M | $3.84M | $19,739.57M |
| 100 MW ★ | $19,744.83M | $26.98M | $4.80M | $19,740.03M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.101 | 100 MW | +7.101 |
| $1.00 | $0.60M | +6.501 | 100 MW | +6.501 |
| $2.00 | $1.20M | +5.901 | 100 MW | +5.901 |
| $2.50 | $1.50M | +5.601 | 100 MW | +5.601 |
| $3.00 | $1.80M | +5.301 | 100 MW | +5.301 |
| $3.50 | $2.10M | +5.001 | 100 MW | +5.001 |
| $4.00 | $2.40M | +4.701 | 100 MW | +4.701 |
| $6.00 | $3.60M | +3.501 | 100 MW | +3.501 |
| $8.00 | $4.80M | +2.301 | 100 MW | +2.301 |
| $12.00 | $7.20M | -0.099 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,737.06M | -0.666 | 57,882 | $4.090M | 1.8% |
| intermediate (1500) | 1,500 | $19,738.88M | +1.148 | 71,741 | $5.551M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,739.93M | +2.199 | 73,939 | $6.287M | 0.7% |
| uncapped (None) | uncapped | $19,740.03M | +2.301 | 74,006 | $6.376M |  |

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
| HOUSTON | $-1.917M | $1.878M | $1.878M | $-1.122M | -0.795 |
| WEST | $-1.917M | $2.136M | $2.136M | $-0.864M | -1.053 |
