# Results tables — `run_n50_2026-05-24_ai_structural_moderate`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,370.34M | $3.83M | $36,362.06M | $36,373.47M |
| 85d | $35,584.87M | $3.83M | $35,576.59M | $35,588.00M |
| 75d | $34,140.59M | $3.83M | $34,132.31M | $34,143.72M |
| 74d | $33,974.28M | $3.83M | $33,965.99M | $33,977.40M |
| 63d | $31,871.59M | $3.83M | $31,863.30M | $31,874.72M |
| 60d | $31,207.31M | $3.83M | $31,199.02M | $31,210.44M |
| 45d | $27,065.15M | $3.83M | $27,056.86M | $27,068.28M |
| 30d | $19,745.28M | $3.83M | $19,737.00M | $19,748.41M |
| 25d | $15,643.79M | $3.83M | $15,635.50M | $15,646.92M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,748.59M | $7.39M | $19,732.09M | $19,753.80M | +0.000 |
| LMP + BESS West | $19,747.68M | $7.04M | $19,731.89M | $19,752.61M | -0.909 |
| LMP + BESS Houston | $19,747.41M | $7.04M | $19,731.70M | $19,752.38M | -1.183 |
| LMP + toll | $19,747.37M | $4.51M | $19,737.58M | $19,750.93M | -1.218 |
| LMP + BESS both | $19,746.50M | $6.69M | $19,731.50M | $19,751.19M | -2.091 |
| LMP + toll + BESS West | $19,746.47M | $4.17M | $19,737.39M | $19,749.79M | -2.126 |
| LMP + toll + BESS Houston | $19,746.19M | $4.18M | $19,737.19M | $19,749.55M | -2.400 |
| LMP + toll + BESS both | $19,745.28M | $3.83M | $19,737.00M | $19,748.41M | -3.309 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $8.244M | $-4.661M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.336M | $1.051M | $-0.000M | $-0.000M | $-1.570M | $-3.000M |
| LMP + BESS West | $2.530M | $1.124M | $-0.000M | $-0.000M | $-1.563M | $-3.000M |
| LMP + BESS both | $5.292M | $1.750M | $-0.000M | $-0.000M | $-3.133M | $-6.000M |
| LMP + toll + BESS Houston | $3.115M | $8.516M | $-4.661M | $-4.800M | $-1.570M | $-3.000M |
| LMP + toll + BESS West | $2.534M | $9.364M | $-4.661M | $-4.800M | $-1.563M | $-3.000M |
| LMP + toll + BESS both | $5.940M | $9.345M | $-4.661M | $-4.800M | $-3.133M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.96 | Mean @ K=$5.96 | Δ vs LMP-only | MW @ K=$5.37 | Mean @ K=$5.37 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,748.59M ★ | +0.000 | n/a | $19,748.59M | +0.000 | n/a | $19,748.59M | +0.000 | n/a | $19,748.59M | +0.000 |
| LMP + toll | 0 MW | $19,748.59M | +0.000 | 60 MW | $19,748.60M ★ | +0.010 | 100 MW | $19,748.95M ★ | +0.358 | 100 MW | $19,749.17M ★ | +0.582 |
| LMP + BESS West | n/a | $19,747.68M | -0.909 | n/a | $19,747.68M | -0.909 | n/a | $19,747.68M | -0.909 | n/a | $19,747.68M | -0.909 |
| LMP + toll + BESS West | 0 MW | $19,747.68M | -0.909 | 60 MW | $19,747.69M | -0.898 | 100 MW | $19,748.04M | -0.551 | 100 MW | $19,748.27M | -0.326 |
| LMP + BESS Houston | n/a | $19,747.41M | -1.183 | n/a | $19,747.41M | -1.183 | n/a | $19,747.41M | -1.183 | n/a | $19,747.41M | -1.183 |
| LMP + toll + BESS Houston | 0 MW | $19,747.41M | -1.183 | 60 MW | $19,747.42M | -1.172 | 100 MW | $19,747.77M | -0.825 | 100 MW | $19,747.99M | -0.600 |
| LMP + BESS both | n/a | $19,746.50M | -2.091 | n/a | $19,746.50M | -2.091 | n/a | $19,746.50M | -2.091 | n/a | $19,746.50M | -2.091 |
| LMP + toll + BESS both | 0 MW | $19,746.50M | -2.091 | 60 MW | $19,746.51M | -2.081 | 100 MW | $19,746.86M | -1.733 | 100 MW | $19,747.08M | -1.509 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.218 | +2.956 | -2.977 | +5.496 |
| LMP + BESS Houston | -1.183 | +0.351 | -1.418 | -0.384 |
| LMP + BESS West | -0.909 | +0.357 | -1.221 | -0.138 |
| LMP + BESS both | -2.091 | +0.702 | -2.614 | -0.549 |
| LMP + toll + BESS Houston | -2.400 | +3.301 | -4.372 | +5.106 |
| LMP + toll + BESS West | -2.126 | +3.303 | -4.119 | +5.248 |
| LMP + toll + BESS both | -3.309 | +3.648 | -5.525 | +4.862 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,748.59M | $7.39M | $0.00M | $19,748.59M |
| 20 MW | $19,749.31M | $6.81M | $0.96M | $19,748.35M |
| 40 MW | $19,750.03M | $6.23M | $1.92M | $19,748.11M |
| 60 MW | $19,750.75M | $5.65M | $2.88M | $19,747.87M |
| 80 MW | $19,751.46M | $5.08M | $3.84M | $19,747.62M |
| 100 MW | $19,752.17M | $4.51M | $4.80M | $19,747.37M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +3.582 | 100 MW | +3.582 |
| $1.00 | $0.60M | +2.982 | 100 MW | +2.982 |
| $2.00 | $1.20M | +2.382 | 100 MW | +2.382 |
| $2.50 | $1.50M | +2.082 | 100 MW | +2.082 |
| $3.00 | $1.80M | +1.782 | 100 MW | +1.782 |
| $3.50 | $2.10M | +1.482 | 100 MW | +1.482 |
| $4.00 | $2.40M | +1.182 | 100 MW | +1.182 |
| $6.00 | $3.60M | -0.018 | 20 MW | +0.001 |
| $8.00 | $4.80M | -1.218 | 0 MW | +0.000 |
| $12.00 | $7.20M | -3.618 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,746.41M | -2.177 | 58,884 | $3.517M | 1.9% |
| intermediate (1500) | 1,500 | $19,747.08M | -1.510 | 73,359 | $4.430M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,747.35M | -1.240 | 75,826 | $4.645M | 0.8% |
| uncapped (None) | uncapped | $19,747.37M | -1.218 | 75,923 | $4.661M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.626M | $0.267M | $1.432M | $2.270M | $1.626M | $3.000M | $-1.374M |
| WEST | 4 | D | $1.884M | $0.277M | $1.607M | $2.516M | $1.884M | $3.000M | $-1.116M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.534M | $0.476M | $0.711M | $0.534M | $-2.466M |
| HOUSTON | 2 | D | $0.974M | $0.863M | $1.321M | $0.974M | $-2.026M |
| HOUSTON | 4 | D | $1.626M | $1.432M | $2.270M | $1.626M | $-1.374M |
| HOUSTON | 8 | D | $2.377M | $2.079M | $3.354M | $2.377M | $-0.623M |
| WEST | 1 | D | $0.610M | $0.524M | $0.794M | $0.610M | $-2.390M |
| WEST | 2 | D | $1.120M | $0.960M | $1.472M | $1.120M | $-1.880M |
| WEST | 4 | D | $1.884M | $1.607M | $2.516M | $1.884M | $-1.116M |
| WEST | 8 | D | $2.737M | $2.308M | $3.681M | $2.737M | $-0.263M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.920M | $1.626M | $1.626M | $-1.374M | -0.547 |
| WEST | $-1.920M | $1.884M | $1.884M | $-1.116M | -0.805 |
