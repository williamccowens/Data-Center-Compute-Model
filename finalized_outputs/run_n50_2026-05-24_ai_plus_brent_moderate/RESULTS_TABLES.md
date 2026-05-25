# Results tables — `run_n50_2026-05-24_ai_plus_brent_moderate`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,369.29M | $3.84M | $36,361.00M | $36,372.47M |
| 85d | $35,583.82M | $3.84M | $35,575.53M | $35,586.99M |
| 75d | $34,139.54M | $3.84M | $34,131.25M | $34,142.71M |
| 74d | $33,973.22M | $3.84M | $33,964.93M | $33,976.40M |
| 63d | $31,870.54M | $3.84M | $31,862.24M | $31,873.71M |
| 60d | $31,206.26M | $3.84M | $31,197.96M | $31,209.43M |
| 45d | $27,064.10M | $3.84M | $27,055.81M | $27,067.27M |
| 30d | $19,744.23M | $3.84M | $19,735.94M | $19,747.40M |
| 25d | $15,642.74M | $3.84M | $15,634.44M | $15,645.91M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,747.37M | $7.40M | $19,730.86M | $19,752.64M | +0.000 |
| LMP + BESS West | $19,746.52M | $7.05M | $19,730.71M | $19,751.50M | -0.853 |
| LMP + BESS Houston | $19,746.24M | $7.05M | $19,730.52M | $19,751.26M | -1.134 |
| LMP + toll | $19,746.22M | $4.52M | $19,736.42M | $19,749.82M | -1.152 |
| LMP + BESS both | $19,745.38M | $6.70M | $19,730.37M | $19,750.12M | -1.987 |
| LMP + toll + BESS West | $19,745.37M | $4.18M | $19,736.28M | $19,748.74M | -2.005 |
| LMP + toll + BESS Houston | $19,745.09M | $4.19M | $19,736.08M | $19,748.49M | -2.286 |
| LMP + toll + BESS both | $19,744.23M | $3.84M | $19,735.94M | $19,747.40M | -3.139 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $8.440M | $-4.792M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.418M | $1.060M | $-0.000M | $-0.000M | $-1.612M | $-3.000M |
| LMP + BESS West | $2.600M | $1.172M | $-0.000M | $-0.000M | $-1.625M | $-3.000M |
| LMP + BESS both | $5.449M | $1.801M | $-0.000M | $-0.000M | $-3.237M | $-6.000M |
| LMP + toll + BESS Houston | $3.199M | $8.718M | $-4.792M | $-4.800M | $-1.612M | $-3.000M |
| LMP + toll + BESS West | $2.604M | $9.607M | $-4.792M | $-4.800M | $-1.625M | $-3.000M |
| LMP + toll + BESS both | $6.139M | $9.551M | $-4.792M | $-4.800M | $-3.237M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$6.07 | Mean @ K=$6.07 | Δ vs LMP-only | MW @ K=$5.47 | Mean @ K=$5.47 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,747.37M ★ | +0.000 | n/a | $19,747.37M | +0.000 | n/a | $19,747.37M | +0.000 | n/a | $19,747.37M | +0.000 |
| LMP + toll | 0 MW | $19,747.37M | +0.000 | 60 MW | $19,747.38M ★ | +0.010 | 100 MW | $19,747.74M ★ | +0.365 | 100 MW | $19,748.02M ★ | +0.648 |
| LMP + BESS West | n/a | $19,746.52M | -0.853 | n/a | $19,746.52M | -0.853 | n/a | $19,746.52M | -0.853 | n/a | $19,746.52M | -0.853 |
| LMP + toll + BESS West | 0 MW | $19,746.52M | -0.853 | 60 MW | $19,746.53M | -0.843 | 100 MW | $19,746.88M | -0.489 | 100 MW | $19,747.17M | -0.205 |
| LMP + BESS Houston | n/a | $19,746.24M | -1.134 | n/a | $19,746.24M | -1.134 | n/a | $19,746.24M | -1.134 | n/a | $19,746.24M | -1.134 |
| LMP + toll + BESS Houston | 0 MW | $19,746.24M | -1.134 | 60 MW | $19,746.25M | -1.123 | 100 MW | $19,746.60M | -0.769 | 100 MW | $19,746.89M | -0.486 |
| LMP + BESS both | n/a | $19,745.38M | -1.987 | n/a | $19,745.38M | -1.987 | n/a | $19,745.38M | -1.987 | n/a | $19,745.38M | -1.987 |
| LMP + toll + BESS both | 0 MW | $19,745.38M | -1.987 | 60 MW | $19,745.39M | -1.977 | 100 MW | $19,745.75M | -1.622 | 100 MW | $19,746.03M | -1.339 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.152 | +2.958 | -2.923 | +5.562 |
| LMP + BESS Houston | -1.134 | +0.351 | -1.371 | -0.334 |
| LMP + BESS West | -0.853 | +0.358 | -1.170 | -0.083 |
| LMP + BESS both | -1.987 | +0.703 | -2.515 | -0.443 |
| LMP + toll + BESS Houston | -2.286 | +3.303 | -4.271 | +5.222 |
| LMP + toll + BESS West | -2.005 | +3.304 | -4.011 | +5.370 |
| LMP + toll + BESS both | -3.139 | +3.650 | -5.370 | +5.035 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,747.37M | $7.40M | $0.00M | $19,747.37M |
| 20 MW | $19,748.11M | $6.82M | $0.96M | $19,747.15M |
| 40 MW | $19,748.84M | $6.24M | $1.92M | $19,746.92M |
| 60 MW | $19,749.57M | $5.66M | $2.88M | $19,746.69M |
| 80 MW | $19,750.29M | $5.09M | $3.84M | $19,746.45M |
| 100 MW | $19,751.02M | $4.52M | $4.80M | $19,746.22M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +3.648 | 100 MW | +3.648 |
| $1.00 | $0.60M | +3.048 | 100 MW | +3.048 |
| $2.00 | $1.20M | +2.448 | 100 MW | +2.448 |
| $2.50 | $1.50M | +2.148 | 100 MW | +2.148 |
| $3.00 | $1.80M | +1.848 | 100 MW | +1.848 |
| $3.50 | $2.10M | +1.548 | 100 MW | +1.548 |
| $4.00 | $2.40M | +1.248 | 100 MW | +1.248 |
| $6.00 | $3.60M | +0.048 | 100 MW | +0.048 |
| $8.00 | $4.80M | -1.152 | 0 MW | +0.000 |
| $12.00 | $7.20M | -3.552 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,745.25M | -2.119 | 58,857 | $3.618M | 1.9% |
| intermediate (1500) | 1,500 | $19,745.93M | -1.445 | 73,341 | $4.557M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,746.20M | -1.175 | 75,824 | $4.776M | 0.8% |
| uncapped (None) | uncapped | $19,746.22M | -1.152 | 75,921 | $4.792M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.671M | $0.268M | $1.474M | $2.316M | $1.671M | $3.000M | $-1.329M |
| WEST | 4 | D | $1.937M | $0.278M | $1.654M | $2.569M | $1.937M | $3.000M | $-1.063M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.549M | $0.490M | $0.727M | $0.549M | $-2.451M |
| HOUSTON | 2 | D | $1.001M | $0.888M | $1.348M | $1.001M | $-1.999M |
| HOUSTON | 4 | D | $1.671M | $1.474M | $2.316M | $1.671M | $-1.329M |
| HOUSTON | 8 | D | $2.442M | $2.140M | $3.424M | $2.442M | $-0.558M |
| WEST | 1 | D | $0.627M | $0.539M | $0.811M | $0.627M | $-2.373M |
| WEST | 2 | D | $1.151M | $0.988M | $1.504M | $1.151M | $-1.849M |
| WEST | 4 | D | $1.937M | $1.654M | $2.569M | $1.937M | $-1.063M |
| WEST | 8 | D | $2.812M | $2.377M | $3.760M | $2.812M | $-0.188M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.894M | $1.671M | $1.671M | $-1.329M | -0.565 |
| WEST | $-1.894M | $1.937M | $1.937M | $-1.063M | -0.831 |
