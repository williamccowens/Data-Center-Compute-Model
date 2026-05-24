# Results tables — `run_n50_2026-05-23_ai_plus_brent_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,091.71M | $24.73M | $148,018.96M | $148,101.59M |
| 90d | $144,741.22M | $24.73M | $144,668.46M | $144,751.10M |
| 85d | $141,544.39M | $24.73M | $141,471.63M | $141,554.26M |
| 75d | $135,563.90M | $24.73M | $135,491.15M | $135,573.78M |
| 74d | $134,879.52M | $24.73M | $134,806.76M | $134,889.40M |
| 63d | $126,268.88M | $24.73M | $126,196.12M | $126,278.76M |
| 60d | $123,557.83M | $24.73M | $123,485.07M | $123,567.70M |
| 45d | $106,455.98M | $24.73M | $106,383.23M | $106,465.86M |
| 30d | $76,109.29M | $24.73M | $76,036.53M | $76,119.16M |
| 25d | $59,071.56M | $24.73M | $58,998.81M | $59,081.44M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $76,110.83M | $26.97M | $76,031.35M | $76,121.58M | +2.419 |
| LMP + toll + BESS West | $76,110.20M | $25.85M | $76,034.12M | $76,120.50M | +1.784 |
| LMP + toll + BESS Houston | $76,109.92M | $25.84M | $76,033.76M | $76,120.25M | +1.508 |
| LMP + toll + BESS both | $76,109.29M | $24.73M | $76,036.53M | $76,119.16M | +0.873 |
| LMP only | $76,108.42M | $41.64M | $75,983.56M | $76,124.35M | +0.000 |
| LMP + BESS West | $76,107.78M | $40.52M | $75,986.24M | $76,123.21M | -0.635 |
| LMP + BESS Houston | $76,107.51M | $40.51M | $75,985.69M | $76,122.97M | -0.910 |
| LMP + BESS both | $76,106.87M | $39.40M | $75,988.36M | $76,121.83M | -1.546 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.774M | $-6.556M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.991M | $1.413M | $-0.000M | $-0.000M | $-2.314M | $-3.000M |
| LMP + BESS West | $3.363M | $1.306M | $-0.000M | $-0.000M | $-2.304M | $-3.000M |
| LMP + BESS both | $6.871M | $2.202M | $-0.000M | $-0.000M | $-4.618M | $-6.000M |
| LMP + toll + BESS Houston | $4.117M | $14.061M | $-6.556M | $-4.800M | $-2.314M | $-3.000M |
| LMP + toll + BESS West | $3.284M | $15.159M | $-6.556M | $-4.800M | $-2.304M | $-3.000M |
| LMP + toll + BESS both | $7.781M | $15.066M | $-6.556M | $-4.800M | $-4.618M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$12.03 | Mean @ K=$12.03 | Δ vs LMP-only | MW @ K=$10.83 | Mean @ K=$10.83 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $76,108.42M ★ | +0.006 | 100 MW | $76,109.14M ★ | +0.722 | 100 MW | $76,110.83M ★ | +2.419 | 100 MW | $76,112.63M ★ | +4.219 |
| LMP only | n/a | $76,108.42M | +0.000 | n/a | $76,108.42M | +0.000 | n/a | $76,108.42M | +0.000 | n/a | $76,108.42M | +0.000 |
| LMP + toll + BESS West | 60 MW | $76,107.79M | -0.629 | 100 MW | $76,108.50M | +0.087 | 100 MW | $76,110.20M | +1.784 | 100 MW | $76,112.00M | +3.584 |
| LMP + BESS West | n/a | $76,107.78M | -0.635 | n/a | $76,107.78M | -0.635 | n/a | $76,107.78M | -0.635 | n/a | $76,107.78M | -0.635 |
| LMP + toll + BESS Houston | 60 MW | $76,107.51M | -0.905 | 100 MW | $76,108.23M | -0.189 | 100 MW | $76,109.92M | +1.508 | 100 MW | $76,111.72M | +3.308 |
| LMP + BESS Houston | n/a | $76,107.51M | -0.910 | n/a | $76,107.51M | -0.910 | n/a | $76,107.51M | -0.910 | n/a | $76,107.51M | -0.910 |
| LMP + toll + BESS both | 60 MW | $76,106.88M | -1.540 | 100 MW | $76,107.59M | -0.824 | 100 MW | $76,109.29M | +0.873 | 100 MW | $76,111.09M | +2.673 |
| LMP + BESS both | n/a | $76,106.87M | -1.546 | n/a | $76,106.87M | -1.546 | n/a | $76,106.87M | -1.546 | n/a | $76,106.87M | -1.546 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.419 | +14.688 | -2.884 | +45.841 |
| LMP + BESS Houston | -0.910 | +1.132 | -1.372 | +2.481 |
| LMP + BESS West | -0.635 | +1.119 | -1.170 | +2.699 |
| LMP + BESS both | -1.546 | +2.246 | -2.515 | +5.081 |
| LMP + toll + BESS Houston | +1.508 | +15.811 | -4.240 | +48.385 |
| LMP + toll + BESS West | +1.784 | +15.803 | -3.975 | +48.565 |
| LMP + toll + BESS both | +0.873 | +16.925 | -5.334 | +51.109 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $76,108.42M | $41.64M | $0.00M | $76,108.42M |
| 20 MW | $76,109.86M | $38.70M | $0.96M | $76,108.90M |
| 40 MW | $76,111.31M | $35.77M | $1.92M | $76,109.39M |
| 60 MW | $76,112.75M | $32.83M | $2.88M | $76,109.87M |
| 80 MW | $76,114.19M | $29.90M | $3.84M | $76,110.35M |
| 100 MW ★ | $76,115.63M | $26.97M | $4.80M | $76,110.83M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.219 | 100 MW | +7.219 |
| $1.00 | $0.60M | +6.619 | 100 MW | +6.619 |
| $2.00 | $1.20M | +6.019 | 100 MW | +6.019 |
| $2.50 | $1.50M | +5.719 | 100 MW | +5.719 |
| $3.00 | $1.80M | +5.419 | 100 MW | +5.419 |
| $3.50 | $2.10M | +5.119 | 100 MW | +5.119 |
| $4.00 | $2.40M | +4.819 | 100 MW | +4.819 |
| $6.00 | $3.60M | +3.619 | 100 MW | +3.619 |
| $8.00 | $4.80M | +2.419 | 100 MW | +2.419 |
| $12.00 | $7.20M | +0.019 | 100 MW | +0.019 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,107.85M | -0.566 | 58,992 | $4.217M | 1.9% |
| intermediate (1500) | 1,500 | $76,109.68M | +1.263 | 73,353 | $5.722M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,110.73M | +2.316 | 75,661 | $6.466M | 0.8% |
| uncapped (None) | uncapped | $76,110.83M | +2.419 | 75,729 | $6.556M |  |

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
| HOUSTON | $-1.874M | $1.915M | $1.915M | $-1.085M | -0.789 |
| WEST | $-1.874M | $2.179M | $2.179M | $-0.821M | -1.053 |
