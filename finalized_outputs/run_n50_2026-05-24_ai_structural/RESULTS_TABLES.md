# Results tables — `run_n50_2026-05-24_ai_structural`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,371.89M | $1.25M | $36,369.84M | $36,373.47M |
| 85d | $35,586.42M | $1.25M | $35,584.37M | $35,588.00M |
| 75d | $34,142.14M | $1.25M | $34,140.09M | $34,143.72M |
| 74d | $33,975.82M | $1.25M | $33,973.77M | $33,977.40M |
| 63d | $31,873.14M | $1.25M | $31,871.09M | $31,874.72M |
| 60d | $31,208.86M | $1.25M | $31,206.80M | $31,210.44M |
| 45d | $27,066.70M | $1.25M | $27,064.65M | $27,068.28M |
| 30d | $19,746.83M | $1.25M | $19,744.78M | $19,748.41M |
| 25d | $15,645.34M | $1.25M | $15,643.28M | $15,646.92M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,751.79M | $1.61M | $19,749.17M | $19,753.80M | +0.000 |
| LMP + BESS West | $19,750.73M | $1.53M | $19,748.24M | $19,752.61M | -1.063 |
| LMP + BESS Houston | $19,750.46M | $1.55M | $19,747.94M | $19,752.38M | -1.333 |
| LMP + BESS both | $19,749.40M | $1.47M | $19,747.01M | $19,751.19M | -2.397 |
| LMP + toll | $19,749.23M | $1.39M | $19,746.94M | $19,750.93M | -2.565 |
| LMP + toll + BESS West | $19,748.16M | $1.31M | $19,746.00M | $19,749.79M | -3.629 |
| LMP + toll + BESS Houston | $19,747.90M | $1.33M | $19,745.71M | $19,749.55M | -3.898 |
| LMP + toll + BESS both | $19,746.83M | $1.25M | $19,744.78M | $19,748.41M | -4.962 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.565M | $-4.330M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.088M | $0.945M | $-0.000M | $-0.000M | $-1.366M | $-3.000M |
| LMP + BESS West | $2.251M | $1.044M | $-0.000M | $-0.000M | $-1.358M | $-3.000M |
| LMP + BESS both | $4.736M | $1.592M | $-0.000M | $-0.000M | $-2.725M | $-6.000M |
| LMP + toll + BESS Houston | $2.758M | $6.840M | $-4.330M | $-4.800M | $-1.366M | $-3.000M |
| LMP + toll + BESS West | $2.255M | $7.605M | $-4.330M | $-4.800M | $-1.358M | $-3.000M |
| LMP + toll + BESS both | $5.316M | $7.577M | $-4.330M | $-4.800M | $-2.725M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.72 | Mean @ K=$3.72 | Δ vs LMP-only | MW @ K=$3.35 | Mean @ K=$3.35 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,751.79M ★ | +0.000 | n/a | $19,751.79M ★ | +0.000 | n/a | $19,751.79M | +0.000 | n/a | $19,751.79M | +0.000 |
| LMP + toll | 0 MW | $19,751.79M | +0.000 | 0 MW | $19,751.79M | +0.000 | 60 MW | $19,751.80M ★ | +0.007 | 100 MW | $19,752.02M ★ | +0.224 |
| LMP + BESS West | n/a | $19,750.73M | -1.063 | n/a | $19,750.73M | -1.063 | n/a | $19,750.73M | -1.063 | n/a | $19,750.73M | -1.063 |
| LMP + toll + BESS West | 0 MW | $19,750.73M | -1.063 | 0 MW | $19,750.73M | -1.063 | 60 MW | $19,750.74M | -1.056 | 100 MW | $19,750.95M | -0.840 |
| LMP + BESS Houston | n/a | $19,750.46M | -1.333 | n/a | $19,750.46M | -1.333 | n/a | $19,750.46M | -1.333 | n/a | $19,750.46M | -1.333 |
| LMP + toll + BESS Houston | 0 MW | $19,750.46M | -1.333 | 0 MW | $19,750.46M | -1.333 | 60 MW | $19,750.47M | -1.326 | 100 MW | $19,750.68M | -1.109 |
| LMP + BESS both | n/a | $19,749.40M | -2.397 | n/a | $19,749.40M | -2.397 | n/a | $19,749.40M | -2.397 | n/a | $19,749.40M | -2.397 |
| LMP + toll + BESS both | 0 MW | $19,749.40M | -2.397 | 0 MW | $19,749.40M | -2.397 | 60 MW | $19,749.40M | -2.389 | 100 MW | $19,749.62M | -2.173 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.565 | +0.324 | -2.977 | -2.099 |
| LMP + BESS Houston | -1.333 | +0.079 | -1.426 | -1.194 |
| LMP + BESS West | -1.063 | +0.095 | -1.221 | -0.914 |
| LMP + BESS both | -2.397 | +0.157 | -2.614 | -2.080 |
| LMP + toll + BESS Houston | -3.898 | +0.398 | -4.372 | -3.320 |
| LMP + toll + BESS West | -3.629 | +0.384 | -4.119 | -2.975 |
| LMP + toll + BESS both | -4.962 | +0.459 | -5.525 | -4.170 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,751.79M | $1.61M | $0.00M | $19,751.79M |
| 20 MW | $19,752.24M | $1.56M | $0.96M | $19,751.28M |
| 40 MW | $19,752.69M | $1.52M | $1.92M | $19,750.77M |
| 60 MW | $19,753.14M | $1.47M | $2.88M | $19,750.26M |
| 80 MW | $19,753.58M | $1.43M | $3.84M | $19,749.74M |
| 100 MW | $19,754.03M | $1.39M | $4.80M | $19,749.23M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.235 | 100 MW | +2.235 |
| $1.00 | $0.60M | +1.635 | 100 MW | +1.635 |
| $2.00 | $1.20M | +1.035 | 100 MW | +1.035 |
| $2.50 | $1.50M | +0.735 | 100 MW | +0.735 |
| $3.00 | $1.80M | +0.435 | 100 MW | +0.435 |
| $3.50 | $2.10M | +0.135 | 100 MW | +0.135 |
| $4.00 | $2.40M | -0.165 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.365 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.565 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.965 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,748.98M | -2.812 | 58,451 | $3.412M | 1.8% |
| intermediate (1500) | 1,500 | $19,749.21M | -2.587 | 72,389 | $4.215M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,749.23M | -2.565 | 74,379 | $4.328M | 0.7% |
| uncapped (None) | uncapped | $19,749.23M | -2.565 | 74,411 | $4.330M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.515M | $0.074M | $1.421M | $1.635M | $1.515M | $3.000M | $-1.485M |
| WEST | 4 | D | $1.771M | $0.094M | $1.607M | $1.913M | $1.771M | $3.000M | $-1.229M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.501M | $0.471M | $0.545M | $0.501M | $-2.499M |
| HOUSTON | 2 | D | $0.912M | $0.853M | $0.987M | $0.912M | $-2.088M |
| HOUSTON | 4 | D | $1.515M | $1.421M | $1.635M | $1.515M | $-1.485M |
| HOUSTON | 8 | D | $2.202M | $2.064M | $2.384M | $2.202M | $-0.798M |
| WEST | 1 | D | $0.577M | $0.524M | $0.628M | $0.577M | $-2.423M |
| WEST | 2 | D | $1.057M | $0.960M | $1.148M | $1.057M | $-1.943M |
| WEST | 4 | D | $1.771M | $1.607M | $1.913M | $1.771M | $-1.229M |
| WEST | 8 | D | $2.558M | $2.308M | $2.762M | $2.558M | $-0.442M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.994M | $1.515M | $1.515M | $-1.485M | -0.509 |
| WEST | $-1.994M | $1.771M | $1.771M | $-1.229M | -0.765 |
