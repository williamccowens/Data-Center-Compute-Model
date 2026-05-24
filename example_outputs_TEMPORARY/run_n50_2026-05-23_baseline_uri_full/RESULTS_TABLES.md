# Results tables — `run_n50_2026-05-23_baseline_uri_full`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,093.09M | $24.73M | $148,020.27M | $148,102.91M |
| 90d | $144,742.59M | $24.73M | $144,669.78M | $144,752.41M |
| 85d | $141,545.76M | $24.73M | $141,472.95M | $141,555.58M |
| 75d | $135,565.28M | $24.73M | $135,492.46M | $135,575.10M |
| 74d | $134,880.90M | $24.73M | $134,808.08M | $134,890.71M |
| 63d | $126,270.25M | $24.73M | $126,197.44M | $126,280.07M |
| 60d | $123,559.20M | $24.73M | $123,486.39M | $123,569.02M |
| 45d | $106,457.36M | $24.73M | $106,384.55M | $106,467.18M |
| 30d | $76,110.66M | $24.73M | $76,037.85M | $76,120.48M |
| 25d | $59,072.94M | $24.73M | $59,000.12M | $59,082.76M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP + toll ★ | $76,112.35M | $26.98M | $76,032.80M | $76,123.04M | +2.297 |
| LMP + toll + BESS West | $76,111.64M | $25.86M | $76,035.49M | $76,121.88M | +1.588 |
| LMP + toll + BESS Houston | $76,111.37M | $25.85M | $76,035.15M | $76,121.63M | +1.321 |
| LMP + toll + BESS both | $76,110.66M | $24.73M | $76,037.85M | $76,120.48M | +0.612 |
| LMP only | $76,110.05M | $41.64M | $75,985.13M | $76,125.91M | +0.000 |
| LMP + BESS West | $76,109.34M | $40.53M | $75,987.73M | $76,124.70M | -0.709 |
| LMP + BESS Houston | $76,109.08M | $40.52M | $75,987.26M | $76,124.47M | -0.976 |
| LMP + BESS both | $76,108.37M | $39.40M | $75,989.79M | $76,123.26M | -1.685 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $13.441M | $-6.344M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $3.007M | $1.275M | $-0.000M | $-0.000M | $-2.258M | $-3.000M |
| LMP + BESS West | $3.125M | $1.387M | $-0.000M | $-0.000M | $-2.221M | $-3.000M |
| LMP + BESS both | $6.822M | $1.972M | $-0.000M | $-0.000M | $-4.480M | $-6.000M |
| LMP + toll + BESS Houston | $3.999M | $13.725M | $-6.344M | $-4.800M | $-2.258M | $-3.000M |
| LMP + toll + BESS West | $3.132M | $14.822M | $-6.344M | $-4.800M | $-2.221M | $-3.000M |
| LMP + toll + BESS both | $7.538M | $14.698M | $-6.344M | $-4.800M | $-4.480M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$11.82 | Mean @ K=$11.82 | Δ vs LMP-only | MW @ K=$10.65 | Mean @ K=$10.65 | Δ vs LMP-only | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP + toll | 60 MW | $76,110.06M ★ | +0.006 | 100 MW | $76,110.76M ★ | +0.710 | 100 MW | $76,112.35M ★ | +2.297 | 100 MW | $76,114.15M ★ | +4.097 |
| LMP only | n/a | $76,110.05M | +0.000 | n/a | $76,110.05M | +0.000 | n/a | $76,110.05M | +0.000 | n/a | $76,110.05M | +0.000 |
| LMP + toll + BESS West | 60 MW | $76,109.35M | -0.703 | 100 MW | $76,110.05M | +0.001 | 100 MW | $76,111.64M | +1.588 | 100 MW | $76,113.44M | +3.388 |
| LMP + BESS West | n/a | $76,109.34M | -0.709 | n/a | $76,109.34M | -0.709 | n/a | $76,109.34M | -0.709 | n/a | $76,109.34M | -0.709 |
| LMP + toll + BESS Houston | 60 MW | $76,109.08M | -0.971 | 100 MW | $76,109.79M | -0.266 | 100 MW | $76,111.37M | +1.321 | 100 MW | $76,113.17M | +3.121 |
| LMP + BESS Houston | n/a | $76,109.08M | -0.976 | n/a | $76,109.08M | -0.976 | n/a | $76,109.08M | -0.976 | n/a | $76,109.08M | -0.976 |
| LMP + toll + BESS both | 60 MW | $76,108.37M | -1.679 | 100 MW | $76,109.08M | -0.975 | 100 MW | $76,110.66M | +0.612 | 100 MW | $76,112.46M | +2.412 |
| LMP + BESS both | n/a | $76,108.37M | -1.685 | n/a | $76,108.37M | -1.685 | n/a | $76,108.37M | -1.685 | n/a | $76,108.37M | -1.685 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | +2.297 | +14.689 | -2.986 | +45.710 |
| LMP + BESS Houston | -0.976 | +1.132 | -1.434 | +2.417 |
| LMP + BESS West | -0.709 | +1.119 | -1.238 | +2.628 |
| LMP + BESS both | -1.685 | +2.247 | -2.646 | +4.943 |
| LMP + toll + BESS Houston | +1.321 | +15.811 | -4.406 | +48.188 |
| LMP + toll + BESS West | +1.588 | +15.804 | -4.150 | +48.361 |
| LMP + toll + BESS both | +0.612 | +16.926 | -5.572 | +50.839 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW | $76,110.05M | $41.64M | $0.00M | $76,110.05M |
| 20 MW | $76,111.47M | $38.71M | $0.96M | $76,110.51M |
| 40 MW | $76,112.89M | $35.77M | $1.92M | $76,110.97M |
| 60 MW | $76,114.31M | $32.84M | $2.88M | $76,111.43M |
| 80 MW | $76,115.73M | $29.91M | $3.84M | $76,111.89M |
| 100 MW ★ | $76,117.15M | $26.98M | $4.80M | $76,112.35M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +7.097 | 100 MW | +7.097 |
| $1.00 | $0.60M | +6.497 | 100 MW | +6.497 |
| $2.00 | $1.20M | +5.897 | 100 MW | +5.897 |
| $2.50 | $1.50M | +5.597 | 100 MW | +5.597 |
| $3.00 | $1.80M | +5.297 | 100 MW | +5.297 |
| $3.50 | $2.10M | +4.997 | 100 MW | +4.997 |
| $4.00 | $2.40M | +4.697 | 100 MW | +4.697 |
| $6.00 | $3.60M | +3.497 | 100 MW | +3.497 |
| $8.00 | $4.80M | +2.297 | 100 MW | +2.297 |
| $12.00 | $7.20M | -0.103 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,109.38M | -0.671 | 58,274 | $4.062M | 1.8% |
| intermediate (1500) | 1,500 | $76,111.20M | +1.143 | 72,271 | $5.520M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,112.25M | +2.195 | 74,479 | $6.255M | 0.7% |
| uncapped (None) | uncapped | $76,112.35M | +2.297 | 74,547 | $6.344M |  |

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
| HOUSTON | $-1.829M | $1.855M | $1.855M | $-1.145M | -0.684 |
| WEST | $-1.829M | $2.110M | $2.110M | $-0.890M | -0.938 |
