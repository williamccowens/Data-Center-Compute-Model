# Results tables — `run_n50_2026-05-24_baseline_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,363.99M | $24.73M | $36,291.15M | $36,373.78M |
| 85d | $35,578.52M | $24.73M | $35,505.68M | $35,588.31M |
| 75d | $34,134.24M | $24.73M | $34,061.40M | $34,144.03M |
| 74d | $33,967.92M | $24.73M | $33,895.08M | $33,977.71M |
| 63d | $31,865.23M | $24.73M | $31,792.39M | $31,875.03M |
| 60d | $31,200.95M | $24.73M | $31,128.11M | $31,210.74M |
| 45d | $27,058.79M | $24.73M | $26,985.96M | $27,068.59M |
| 30d | $19,738.92M | $24.73M | $19,666.09M | $19,748.72M |
| 25d | $15,637.43M | $24.73M | $15,564.59M | $15,647.22M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $19,740.61M | $26.98M | $19,661.04M | $19,751.27M | +2.268 |
| LMP + toll + BESS West | $19,739.90M | $25.86M | $19,663.73M | $19,750.11M | +1.560 |
| LMP + toll + BESS Houston | $19,739.63M | $25.85M | $19,663.39M | $19,749.87M | +1.292 |
| LMP + toll + BESS both | $19,738.92M | $24.73M | $19,666.09M | $19,748.72M | +0.583 |
| LMP only | $19,738.34M | $41.65M | $19,613.38M | $19,754.19M | +0.000 |
| LMP + BESS West | $19,737.63M | $40.53M | $19,615.99M | $19,752.99M | -0.709 |
| LMP + BESS Houston | $19,737.36M | $40.52M | $19,615.55M | $19,752.75M | -0.976 |
| LMP + BESS both | $19,736.66M | $39.40M | $19,618.08M | $19,751.54M | -1.685 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.380M | $-6.311M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $3.006M | $1.276M | $-0.000M | $-0.000M | $-2.258M | $-3.000M |
| LMP + BESS West | $3.120M | $1.393M | $-0.000M | $-0.000M | $-2.221M | $-3.000M |
| LMP + BESS both | $6.802M | $1.992M | $-0.000M | $-0.000M | $-4.480M | $-6.000M |
| LMP + toll + BESS Houston | $4.007M | $13.655M | $-6.311M | $-4.800M | $-2.258M | $-3.000M |
| LMP + toll + BESS West | $3.181M | $14.712M | $-6.311M | $-4.800M | $-2.221M | $-3.000M |
| LMP + toll + BESS both | $7.540M | $14.634M | $-6.311M | $-4.800M | $-4.480M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.78 | Mean @ K=$11.78 | Δ vs LMP-only | MW @ K=$10.60 | Mean @ K=$10.60 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $19,738.35M ★ | +0.007 | 100 MW | $19,739.05M ★ | +0.707 | 100 MW | $19,740.61M ★ | +2.268 | 100 MW | $19,742.41M ★ | +4.068 |
| LMP only | n/a | $19,738.34M | +0.000 | n/a | $19,738.34M | +0.000 | n/a | $19,738.34M | +0.000 | n/a | $19,738.34M | +0.000 |
| LMP + toll + BESS West | 60 MW | $19,737.64M | -0.702 | 100 MW | $19,738.34M | -0.002 | 100 MW | $19,739.90M | +1.560 | 100 MW | $19,741.70M | +3.360 |
| LMP + BESS West | n/a | $19,737.63M | -0.709 | n/a | $19,737.63M | -0.709 | n/a | $19,737.63M | -0.709 | n/a | $19,737.63M | -0.709 |
| LMP + toll + BESS Houston | 60 MW | $19,737.37M | -0.969 | 100 MW | $19,738.07M | -0.269 | 100 MW | $19,739.63M | +1.292 | 100 MW | $19,741.43M | +3.092 |
| LMP + BESS Houston | n/a | $19,737.36M | -0.976 | n/a | $19,737.36M | -0.976 | n/a | $19,737.36M | -0.976 | n/a | $19,737.36M | -0.976 |
| LMP + toll + BESS both | 60 MW | $19,736.66M | -1.678 | 100 MW | $19,737.36M | -0.978 | 100 MW | $19,738.92M | +0.583 | 100 MW | $19,740.72M | +2.383 |
| LMP + BESS both | n/a | $19,736.66M | -1.685 | n/a | $19,736.66M | -1.685 | n/a | $19,736.66M | -1.685 | n/a | $19,736.66M | -1.685 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.268 | +14.689 | -3.024 | +45.676 |
| LMP + BESS Houston | -0.976 | +1.132 | -1.434 | +2.417 |
| LMP + BESS West | -0.709 | +1.119 | -1.238 | +2.628 |
| LMP + BESS both | -1.685 | +2.247 | -2.646 | +4.943 |
| LMP + toll + BESS Houston | +1.292 | +15.811 | -4.436 | +48.153 |
| LMP + toll + BESS West | +1.560 | +15.804 | -4.184 | +48.327 |
| LMP + toll + BESS both | +0.583 | +16.926 | -5.606 | +50.804 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $19,738.34M | $41.65M | $0.00M | $19,738.34M |
| 20 MW | $19,739.76M | $38.71M | $0.96M | $19,738.80M |
| 40 MW | $19,741.17M | $35.78M | $1.92M | $19,739.25M |
| 60 MW | $19,742.59M | $32.84M | $2.88M | $19,739.71M |
| 80 MW | $19,744.00M | $29.91M | $3.84M | $19,740.16M |
| 100 MW ★ | $19,745.41M | $26.98M | $4.80M | $19,740.61M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.068 | 100 MW | +7.068 |
| $1.00 | $0.60M | +6.468 | 100 MW | +6.468 |
| $2.00 | $1.20M | +5.868 | 100 MW | +5.868 |
| $2.50 | $1.50M | +5.568 | 100 MW | +5.568 |
| $3.00 | $1.80M | +5.268 | 100 MW | +5.268 |
| $3.50 | $2.10M | +4.968 | 100 MW | +4.968 |
| $4.00 | $2.40M | +4.668 | 100 MW | +4.668 |
| $6.00 | $3.60M | +3.468 | 100 MW | +3.468 |
| $8.00 | $4.80M | +2.268 | 100 MW | +2.268 |
| $12.00 | $7.20M | -0.132 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,737.65M | -0.695 | 57,880 | $4.039M | 1.8% |
| intermediate (1500) | 1,500 | $19,739.46M | +1.115 | 71,734 | $5.488M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,740.51M | +2.166 | 73,925 | $6.222M | 0.7% |
| uncapped (None) | uncapped | $19,740.61M | +2.268 | 73,992 | $6.311M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.855M | $1.077M | $1.418M | $4.929M | $1.855M | $3.000M | $-1.145M |
| WEST | 4 | D | $2.110M | $1.072M | $1.591M | $5.233M | $2.110M | $3.000M | $-0.890M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.598M | $0.471M | $1.514M | $0.598M | $-2.402M |
| HOUSTON | 2 | D | $1.098M | $0.854M | $2.827M | $1.098M | $-1.902M |
| HOUSTON | 4 | D | $1.855M | $1.418M | $4.929M | $1.855M | $-1.145M |
| HOUSTON | 8 | D | $2.738M | $2.058M | $7.468M | $2.738M | $-0.262M |
| WEST | 1 | D | $0.674M | $0.519M | $1.590M | $0.674M | $-2.326M |
| WEST | 2 | D | $1.241M | $0.950M | $2.991M | $1.241M | $-1.759M |
| WEST | 4 | D | $2.110M | $1.591M | $5.233M | $2.110M | $-0.890M |
| WEST | 8 | D | $3.094M | $2.285M | $7.903M | $3.094M | $0.094M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.839M | $1.855M | $1.855M | $-1.145M | -0.694 |
| WEST | $-1.839M | $2.110M | $2.110M | $-0.890M | -0.948 |
