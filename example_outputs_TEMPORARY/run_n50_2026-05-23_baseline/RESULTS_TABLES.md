# Results tables — `run_n50_2026-05-23_baseline`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 95d ★ | $148,101.32M | $1.25M | $148,099.28M | $148,102.91M |
| 90d | $144,750.82M | $1.25M | $144,748.79M | $144,752.41M |
| 85d | $141,553.99M | $1.25M | $141,551.96M | $141,555.58M |
| 75d | $135,573.50M | $1.25M | $135,571.47M | $135,575.10M |
| 74d | $134,889.12M | $1.25M | $134,887.09M | $134,890.71M |
| 63d | $126,278.48M | $1.25M | $126,276.45M | $126,280.07M |
| 60d | $123,567.43M | $1.25M | $123,565.40M | $123,569.02M |
| 45d | $106,465.59M | $1.25M | $106,463.56M | $106,467.18M |
| 30d | $76,118.89M | $1.25M | $76,116.86M | $76,120.48M |
| 25d | $59,081.16M | $1.25M | $59,079.13M | $59,082.76M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $76,123.91M | $1.61M | $76,121.33M | $76,125.91M | +0.000 |
| LMP + BESS West | $76,122.83M | $1.53M | $76,120.38M | $76,124.70M | -1.082 |
| LMP + BESS Houston | $76,122.56M | $1.54M | $76,120.09M | $76,124.47M | -1.350 |
| LMP + BESS both | $76,121.48M | $1.46M | $76,119.14M | $76,123.26M | -2.431 |
| LMP + toll | $76,121.32M | $1.38M | $76,119.06M | $76,123.04M | -2.591 |
| LMP + toll + BESS West | $76,120.24M | $1.30M | $76,118.11M | $76,121.88M | -3.673 |
| LMP + toll + BESS Houston | $76,119.97M | $1.33M | $76,117.81M | $76,121.63M | -3.941 |
| LMP + toll + BESS both | $76,118.89M | $1.25M | $76,116.86M | $76,120.48M | -5.023 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.489M | $-4.280M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.046M | $0.957M | $-0.000M | $-0.000M | $-1.352M | $-3.000M |
| LMP + BESS West | $2.203M | $1.053M | $-0.000M | $-0.000M | $-1.338M | $-3.000M |
| LMP + BESS both | $4.672M | $1.587M | $-0.000M | $-0.000M | $-2.690M | $-6.000M |
| LMP + toll + BESS Houston | $2.719M | $6.772M | $-4.280M | $-4.800M | $-1.352M | $-3.000M |
| LMP + toll + BESS West | $2.200M | $7.544M | $-4.280M | $-4.800M | $-1.338M | $-3.000M |
| LMP + toll + BESS both | $5.242M | $7.505M | $-4.280M | $-4.800M | $-2.690M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.68 | Mean @ K=$3.68 | Δ vs LMP-only | MW @ K=$3.31 | Mean @ K=$3.31 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $76,123.91M ★ | +0.000 | n/a | $76,123.91M ★ | +0.000 | n/a | $76,123.91M | +0.000 | n/a | $76,123.91M | +0.000 |
| LMP + toll | 0 MW | $76,123.91M | +0.000 | 0 MW | $76,123.91M | +0.000 | 60 MW | $76,123.92M ★ | +0.005 | 100 MW | $76,124.13M ★ | +0.221 |
| LMP + BESS West | n/a | $76,122.83M | -1.082 | n/a | $76,122.83M | -1.082 | n/a | $76,122.83M | -1.082 | n/a | $76,122.83M | -1.082 |
| LMP + toll + BESS West | 0 MW | $76,122.83M | -1.082 | 0 MW | $76,122.83M | -1.082 | 60 MW | $76,122.84M | -1.077 | 100 MW | $76,123.05M | -0.861 |
| LMP + BESS Houston | n/a | $76,122.56M | -1.350 | n/a | $76,122.56M | -1.350 | n/a | $76,122.56M | -1.350 | n/a | $76,122.56M | -1.350 |
| LMP + toll + BESS Houston | 0 MW | $76,122.56M | -1.350 | 0 MW | $76,122.56M | -1.350 | 60 MW | $76,122.57M | -1.344 | 100 MW | $76,122.78M | -1.129 |
| LMP + BESS both | n/a | $76,121.48M | -2.431 | n/a | $76,121.48M | -2.431 | n/a | $76,121.48M | -2.431 | n/a | $76,121.48M | -2.431 |
| LMP + toll + BESS both | 0 MW | $76,121.48M | -2.431 | 0 MW | $76,121.48M | -2.431 | 60 MW | $76,121.49M | -2.426 | 100 MW | $76,121.70M | -2.210 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.591 | +0.319 | -2.986 | -2.120 |
| LMP + BESS Houston | -1.350 | +0.078 | -1.442 | -1.212 |
| LMP + BESS West | -1.082 | +0.094 | -1.238 | -0.934 |
| LMP + BESS both | -2.431 | +0.156 | -2.646 | -2.118 |
| LMP + toll + BESS Houston | -3.941 | +0.392 | -4.406 | -3.361 |
| LMP + toll + BESS West | -3.673 | +0.378 | -4.150 | -3.035 |
| LMP + toll + BESS both | -5.023 | +0.452 | -5.572 | -4.247 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $76,123.91M | $1.61M | $0.00M | $76,123.91M |
| 20 MW | $76,124.36M | $1.56M | $0.96M | $76,123.40M |
| 40 MW | $76,124.80M | $1.51M | $1.92M | $76,122.88M |
| 60 MW | $76,125.24M | $1.47M | $2.88M | $76,122.36M |
| 80 MW | $76,125.68M | $1.43M | $3.84M | $76,121.84M |
| 100 MW | $76,126.12M | $1.38M | $4.80M | $76,121.32M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.209 | 100 MW | +2.209 |
| $1.00 | $0.60M | +1.609 | 100 MW | +1.609 |
| $2.00 | $1.20M | +1.009 | 100 MW | +1.009 |
| $2.50 | $1.50M | +0.709 | 100 MW | +0.709 |
| $3.00 | $1.80M | +0.409 | 100 MW | +0.409 |
| $3.50 | $2.10M | +0.109 | 100 MW | +0.109 |
| $4.00 | $2.40M | -0.191 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.391 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.591 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.991 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $76,121.08M | -2.833 | 58,071 | $3.381M | 1.8% |
| intermediate (1500) | 1,500 | $76,121.30M | -2.612 | 71,777 | $4.168M | 1.1% |
| near-nameplate (2280) | 2,280 | $76,121.32M | -2.591 | 73,702 | $4.278M | 0.7% |
| uncapped (None) | uncapped | $76,121.32M | -2.591 | 73,733 | $4.280M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.500M | $0.074M | $1.406M | $1.619M | $1.500M | $3.000M | $-1.500M |
| WEST | 4 | D | $1.753M | $0.093M | $1.591M | $1.894M | $1.753M | $3.000M | $-1.247M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.496M | $0.466M | $0.540M | $0.496M | $-2.504M |
| HOUSTON | 2 | D | $0.903M | $0.845M | $0.977M | $0.903M | $-2.097M |
| HOUSTON | 4 | D | $1.500M | $1.406M | $1.619M | $1.500M | $-1.500M |
| HOUSTON | 8 | D | $2.180M | $2.043M | $2.360M | $2.180M | $-0.820M |
| WEST | 1 | D | $0.571M | $0.519M | $0.622M | $0.571M | $-2.429M |
| WEST | 2 | D | $1.046M | $0.950M | $1.136M | $1.046M | $-1.954M |
| WEST | 4 | D | $1.753M | $1.591M | $1.894M | $1.753M | $-1.247M |
| WEST | 8 | D | $2.533M | $2.285M | $2.735M | $2.533M | $-0.467M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-2.009M | $1.500M | $1.500M | $-1.500M | -0.509 |
| WEST | $-2.009M | $1.753M | $1.753M | $-1.247M | -0.763 |
