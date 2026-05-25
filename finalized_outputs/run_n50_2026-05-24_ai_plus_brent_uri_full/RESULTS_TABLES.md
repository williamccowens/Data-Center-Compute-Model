# Results tables — `run_n50_2026-05-24_ai_plus_brent_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,362.62M | $24.73M | $36,289.84M | $36,372.47M |
| 85d | $35,577.15M | $24.73M | $35,504.36M | $35,586.99M |
| 75d | $34,132.87M | $24.73M | $34,060.08M | $34,142.71M |
| 74d | $33,966.55M | $24.73M | $33,893.77M | $33,976.40M |
| 63d | $31,863.86M | $24.73M | $31,791.08M | $31,873.71M |
| 60d | $31,199.58M | $24.73M | $31,126.80M | $31,209.43M |
| 45d | $27,057.42M | $24.73M | $26,984.64M | $27,067.27M |
| 30d | $19,737.55M | $24.73M | $19,664.77M | $19,747.40M |
| 25d | $15,636.06M | $24.73M | $15,563.28M | $15,645.91M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $19,739.10M | $26.97M | $19,659.59M | $19,749.82M | +2.389 |
| LMP + toll + BESS West | $19,738.46M | $25.85M | $19,662.36M | $19,748.74M | +1.754 |
| LMP + toll + BESS Houston | $19,738.19M | $25.85M | $19,662.00M | $19,748.49M | +1.478 |
| LMP + toll + BESS both | $19,737.55M | $24.73M | $19,664.77M | $19,747.40M | +0.843 |
| LMP only | $19,736.71M | $41.64M | $19,611.82M | $19,752.64M | +0.000 |
| LMP + BESS West | $19,736.08M | $40.52M | $19,614.50M | $19,751.50M | -0.635 |
| LMP + BESS Houston | $19,735.80M | $40.51M | $19,613.99M | $19,751.26M | -0.910 |
| LMP + BESS both | $19,735.17M | $39.40M | $19,616.62M | $19,750.12M | -1.546 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.713M | $-6.524M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.995M | $1.409M | $-0.000M | $-0.000M | $-2.314M | $-3.000M |
| LMP + BESS West | $3.324M | $1.345M | $-0.000M | $-0.000M | $-2.304M | $-3.000M |
| LMP + BESS both | $7.038M | $2.035M | $-0.000M | $-0.000M | $-4.618M | $-6.000M |
| LMP + toll + BESS Houston | $4.123M | $13.994M | $-6.524M | $-4.800M | $-2.314M | $-3.000M |
| LMP + toll + BESS West | $3.273M | $15.109M | $-6.524M | $-4.800M | $-2.304M | $-3.000M |
| LMP + toll + BESS both | $7.690M | $15.096M | $-6.524M | $-4.800M | $-4.618M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.98 | Mean @ K=$11.98 | Δ vs LMP-only | MW @ K=$10.78 | Mean @ K=$10.78 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $19,736.72M ★ | +0.007 | 100 MW | $19,737.43M ★ | +0.719 | 100 MW | $19,739.10M ★ | +2.389 | 100 MW | $19,740.90M ★ | +4.189 |
| LMP only | n/a | $19,736.71M | +0.000 | n/a | $19,736.71M | +0.000 | n/a | $19,736.71M | +0.000 | n/a | $19,736.71M | +0.000 |
| LMP + toll + BESS West | 60 MW | $19,736.08M | -0.628 | 100 MW | $19,736.79M | +0.084 | 100 MW | $19,738.46M | +1.754 | 100 MW | $19,740.26M | +3.554 |
| LMP + BESS West | n/a | $19,736.08M | -0.635 | n/a | $19,736.08M | -0.635 | n/a | $19,736.08M | -0.635 | n/a | $19,736.08M | -0.635 |
| LMP + toll + BESS Houston | 60 MW | $19,735.81M | -0.903 | 100 MW | $19,736.52M | -0.192 | 100 MW | $19,738.19M | +1.478 | 100 MW | $19,739.99M | +3.278 |
| LMP + BESS Houston | n/a | $19,735.80M | -0.910 | n/a | $19,735.80M | -0.910 | n/a | $19,735.80M | -0.910 | n/a | $19,735.80M | -0.910 |
| LMP + toll + BESS both | 60 MW | $19,735.17M | -1.539 | 100 MW | $19,735.88M | -0.827 | 100 MW | $19,737.55M | +0.843 | 100 MW | $19,739.35M | +2.643 |
| LMP + BESS both | n/a | $19,735.17M | -1.546 | n/a | $19,735.17M | -1.546 | n/a | $19,735.17M | -1.546 | n/a | $19,735.17M | -1.546 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.389 | +14.689 | -2.923 | +45.805 |
| LMP + BESS Houston | -0.910 | +1.132 | -1.372 | +2.481 |
| LMP + BESS West | -0.635 | +1.119 | -1.170 | +2.699 |
| LMP + BESS both | -1.546 | +2.246 | -2.515 | +5.081 |
| LMP + toll + BESS Houston | +1.478 | +15.811 | -4.271 | +48.350 |
| LMP + toll + BESS West | +1.754 | +15.803 | -4.011 | +48.529 |
| LMP + toll + BESS both | +0.843 | +16.925 | -5.370 | +51.074 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $19,736.71M | $41.64M | $0.00M | $19,736.71M |
| 20 MW | $19,738.15M | $38.70M | $0.96M | $19,737.19M |
| 40 MW | $19,739.59M | $35.77M | $1.92M | $19,737.67M |
| 60 MW | $19,741.03M | $32.84M | $2.88M | $19,738.15M |
| 80 MW | $19,742.47M | $29.90M | $3.84M | $19,738.63M |
| 100 MW ★ | $19,743.90M | $26.97M | $4.80M | $19,739.10M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.189 | 100 MW | +7.189 |
| $1.00 | $0.60M | +6.589 | 100 MW | +6.589 |
| $2.00 | $1.20M | +5.989 | 100 MW | +5.989 |
| $2.50 | $1.50M | +5.689 | 100 MW | +5.689 |
| $3.00 | $1.80M | +5.389 | 100 MW | +5.389 |
| $3.50 | $2.10M | +5.089 | 100 MW | +5.089 |
| $4.00 | $2.40M | +4.789 | 100 MW | +4.789 |
| $6.00 | $3.60M | +3.589 | 100 MW | +3.589 |
| $8.00 | $4.80M | +2.389 | 100 MW | +2.389 |
| $12.00 | $7.20M | -0.011 | 20 MW | +0.001 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,736.12M | -0.592 | 58,622 | $4.195M | 1.8% |
| intermediate (1500) | 1,500 | $19,737.94M | +1.234 | 72,855 | $5.692M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,739.00M | +2.286 | 75,147 | $6.435M | 0.7% |
| uncapped (None) | uncapped | $19,739.10M | +2.389 | 75,215 | $6.524M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.915M | $1.076M | $1.474M | $4.986M | $1.915M | $3.000M | $-1.085M |
| WEST | 4 | D | $2.179M | $1.072M | $1.654M | $5.302M | $2.179M | $3.000M | $-0.821M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.618M | $0.490M | $1.533M | $0.618M | $-2.382M |
| HOUSTON | 2 | D | $1.134M | $0.888M | $2.860M | $1.134M | $-1.866M |
| HOUSTON | 4 | D | $1.915M | $1.474M | $4.986M | $1.915M | $-1.085M |
| HOUSTON | 8 | D | $2.825M | $2.140M | $7.551M | $2.825M | $-0.175M |
| WEST | 1 | D | $0.697M | $0.539M | $1.612M | $0.697M | $-2.303M |
| WEST | 2 | D | $1.283M | $0.988M | $3.032M | $1.283M | $-1.717M |
| WEST | 4 | D | $2.179M | $1.654M | $5.302M | $2.179M | $-0.821M |
| WEST | 8 | D | $3.195M | $2.377M | $7.997M | $3.195M | $0.195M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.790M | $1.915M | $1.915M | $-1.085M | -0.705 |
| WEST | $-1.790M | $2.179M | $2.179M | $-0.821M | -0.970 |
