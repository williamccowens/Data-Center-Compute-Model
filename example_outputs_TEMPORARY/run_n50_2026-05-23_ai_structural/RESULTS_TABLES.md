# Results tables — `run_n50_2026-05-23_ai_structural`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,101.00M | $1.26M | $148,098.95M | $148,102.60M |
| 90d | $144,750.50M | $1.26M | $144,748.45M | $144,752.11M |
| 85d | $141,553.67M | $1.26M | $141,551.62M | $141,555.27M |
| 75d | $135,573.19M | $1.26M | $135,571.14M | $135,574.79M |
| 74d | $134,888.80M | $1.26M | $134,886.76M | $134,890.41M |
| 63d | $126,278.16M | $1.26M | $126,276.11M | $126,279.77M |
| 60d | $123,567.11M | $1.26M | $123,565.06M | $123,568.72M |
| 45d | $106,465.27M | $1.26M | $106,463.22M | $106,466.87M |
| 30d | $76,118.57M | $1.26M | $76,116.52M | $76,120.18M |
| 25d | $59,080.84M | $1.26M | $59,078.80M | $59,082.45M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $76,123.50M | $1.62M | $76,120.90M | $76,125.52M | +0.000 |
| LMP + BESS West | $76,122.44M | $1.54M | $76,119.96M | $76,124.33M | -1.063 |
| LMP + BESS Houston | $76,122.17M | $1.56M | $76,119.67M | $76,124.09M | -1.333 |
| LMP + BESS both | $76,121.11M | $1.48M | $76,118.74M | $76,122.90M | -2.397 |
| LMP + toll | $76,120.97M | $1.40M | $76,118.68M | $76,122.69M | -2.536 |
| LMP + toll + BESS West | $76,119.90M | $1.32M | $76,117.75M | $76,121.56M | -3.599 |
| LMP + toll + BESS Houston | $76,119.63M | $1.34M | $76,117.46M | $76,121.31M | -3.869 |
| LMP + toll + BESS both | $76,118.57M | $1.26M | $76,116.52M | $76,120.18M | -4.932 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.626M | $-4.362M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.072M | $0.961M | $-0.000M | $-0.000M | $-1.366M | $-3.000M |
| LMP + BESS West | $2.232M | $1.063M | $-0.000M | $-0.000M | $-1.358M | $-3.000M |
| LMP + BESS both | $4.727M | $1.601M | $-0.000M | $-0.000M | $-2.725M | $-6.000M |
| LMP + toll + BESS Houston | $2.752M | $6.907M | $-4.362M | $-4.800M | $-1.366M | $-3.000M |
| LMP + toll + BESS West | $2.236M | $7.685M | $-4.362M | $-4.800M | $-1.358M | $-3.000M |
| LMP + toll + BESS both | $5.306M | $7.648M | $-4.362M | $-4.800M | $-2.725M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.77 | Mean @ K=$3.77 | Δ vs LMP-only | MW @ K=$3.40 | Mean @ K=$3.40 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $76,123.50M ★ | +0.000 | n/a | $76,123.50M ★ | +0.000 | n/a | $76,123.50M | +0.000 | n/a | $76,123.50M | +0.000 |
| LMP + toll | 0 MW | $76,123.50M | +0.000 | 0 MW | $76,123.50M | +0.000 | 60 MW | $76,123.51M ★ | +0.005 | 100 MW | $76,123.73M ★ | +0.226 |
| LMP + BESS West | n/a | $76,122.44M | -1.063 | n/a | $76,122.44M | -1.063 | n/a | $76,122.44M | -1.063 | n/a | $76,122.44M | -1.063 |
| LMP + toll + BESS West | 0 MW | $76,122.44M | -1.063 | 0 MW | $76,122.44M | -1.063 | 60 MW | $76,122.45M | -1.058 | 100 MW | $76,122.67M | -0.837 |
| LMP + BESS Houston | n/a | $76,122.17M | -1.333 | n/a | $76,122.17M | -1.333 | n/a | $76,122.17M | -1.333 | n/a | $76,122.17M | -1.333 |
| LMP + toll + BESS Houston | 0 MW | $76,122.17M | -1.333 | 0 MW | $76,122.17M | -1.333 | 60 MW | $76,122.18M | -1.328 | 100 MW | $76,122.40M | -1.107 |
| LMP + BESS both | n/a | $76,121.11M | -2.397 | n/a | $76,121.11M | -2.397 | n/a | $76,121.11M | -2.397 | n/a | $76,121.11M | -2.397 |
| LMP + toll + BESS both | 0 MW | $76,121.11M | -2.397 | 0 MW | $76,121.11M | -2.397 | 60 MW | $76,121.11M | -2.391 | 100 MW | $76,121.33M | -2.170 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.536 | +0.325 | -2.940 | -2.056 |
| LMP + BESS Houston | -1.333 | +0.079 | -1.426 | -1.194 |
| LMP + BESS West | -1.063 | +0.095 | -1.221 | -0.914 |
| LMP + BESS both | -2.397 | +0.157 | -2.614 | -2.080 |
| LMP + toll + BESS Houston | -3.869 | +0.399 | -4.342 | -3.278 |
| LMP + toll + BESS West | -3.599 | +0.385 | -4.083 | -2.950 |
| LMP + toll + BESS both | -4.932 | +0.459 | -5.489 | -4.145 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $76,123.50M | $1.62M | $0.00M | $76,123.50M |
| 20 MW | $76,123.96M | $1.57M | $0.96M | $76,123.00M |
| 40 MW | $76,124.41M | $1.53M | $1.92M | $76,122.49M |
| 60 MW | $76,124.87M | $1.48M | $2.88M | $76,121.99M |
| 80 MW | $76,125.32M | $1.44M | $3.84M | $76,121.48M |
| 100 MW | $76,125.77M | $1.40M | $4.80M | $76,120.97M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.264 | 100 MW | +2.264 |
| $1.00 | $0.60M | +1.664 | 100 MW | +1.664 |
| $2.00 | $1.20M | +1.064 | 100 MW | +1.064 |
| $2.50 | $1.50M | +0.764 | 100 MW | +0.764 |
| $3.00 | $1.80M | +0.464 | 100 MW | +0.464 |
| $3.50 | $2.10M | +0.164 | 100 MW | +0.164 |
| $4.00 | $2.40M | -0.136 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.336 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.536 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.936 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,120.72M | -2.787 | 58,833 | $3.434M | 1.9% |
| intermediate (1500) | 1,500 | $76,120.95M | -2.558 | 72,919 | $4.246M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,120.97M | -2.536 | 74,928 | $4.361M | 0.7% |
| uncapped (None) | uncapped | $76,120.97M | -2.536 | 74,959 | $4.362M |  |

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
| HOUSTON | $-1.999M | $1.515M | $1.515M | $-1.485M | -0.514 |
| WEST | $-1.999M | $1.771M | $1.771M | $-1.229M | -0.770 |
