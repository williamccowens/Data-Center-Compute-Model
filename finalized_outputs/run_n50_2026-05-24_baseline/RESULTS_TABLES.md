# Results tables — `run_n50_2026-05-24_baseline`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,372.21M | $1.24M | $36,370.17M | $36,373.78M |
| 85d | $35,586.74M | $1.24M | $35,584.70M | $35,588.31M |
| 75d | $34,142.46M | $1.24M | $34,140.42M | $34,144.03M |
| 74d | $33,976.14M | $1.24M | $33,974.10M | $33,977.71M |
| 63d | $31,873.46M | $1.24M | $31,871.42M | $31,875.03M |
| 60d | $31,209.18M | $1.24M | $31,207.14M | $31,210.74M |
| 45d | $27,067.02M | $1.24M | $27,064.98M | $27,068.59M |
| 30d | $19,747.15M | $1.24M | $19,745.11M | $19,748.72M |
| 25d | $15,645.66M | $1.24M | $15,643.62M | $15,647.22M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,752.20M | $1.60M | $19,749.60M | $19,754.19M | +0.000 |
| LMP + BESS West | $19,751.12M | $1.52M | $19,748.65M | $19,752.99M | -1.082 |
| LMP + BESS Houston | $19,750.85M | $1.53M | $19,748.36M | $19,752.75M | -1.350 |
| LMP + BESS both | $19,749.77M | $1.46M | $19,747.41M | $19,751.54M | -2.431 |
| LMP + toll | $19,749.58M | $1.38M | $19,747.31M | $19,751.27M | -2.620 |
| LMP + toll + BESS West | $19,748.50M | $1.30M | $19,746.36M | $19,750.11M | -3.702 |
| LMP + toll + BESS Houston | $19,748.23M | $1.32M | $19,746.06M | $19,749.87M | -3.969 |
| LMP + toll + BESS both | $19,747.15M | $1.24M | $19,745.11M | $19,748.72M | -5.051 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.427M | $-4.247M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.070M | $0.932M | $-0.000M | $-0.000M | $-1.352M | $-3.000M |
| LMP + BESS West | $2.224M | $1.032M | $-0.000M | $-0.000M | $-1.338M | $-3.000M |
| LMP + BESS both | $4.692M | $1.567M | $-0.000M | $-0.000M | $-2.690M | $-6.000M |
| LMP + toll + BESS Houston | $2.728M | $6.702M | $-4.247M | $-4.800M | $-1.352M | $-3.000M |
| LMP + toll + BESS West | $2.230M | $7.453M | $-4.247M | $-4.800M | $-1.338M | $-3.000M |
| LMP + toll + BESS both | $5.251M | $7.435M | $-4.247M | $-4.800M | $-2.690M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.63 | Mean @ K=$3.63 | Δ vs LMP-only | MW @ K=$3.27 | Mean @ K=$3.27 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,752.20M ★ | +0.000 | n/a | $19,752.20M ★ | +0.000 | n/a | $19,752.20M | +0.000 | n/a | $19,752.20M | +0.000 |
| LMP + toll | 0 MW | $19,752.20M | +0.000 | 0 MW | $19,752.20M | +0.000 | 60 MW | $19,752.21M ★ | +0.007 | 100 MW | $19,752.42M ★ | +0.218 |
| LMP + BESS West | n/a | $19,751.12M | -1.082 | n/a | $19,751.12M | -1.082 | n/a | $19,751.12M | -1.082 | n/a | $19,751.12M | -1.082 |
| LMP + toll + BESS West | 0 MW | $19,751.12M | -1.082 | 0 MW | $19,751.12M | -1.082 | 60 MW | $19,751.13M | -1.075 | 100 MW | $19,751.34M | -0.864 |
| LMP + BESS Houston | n/a | $19,750.85M | -1.350 | n/a | $19,750.85M | -1.350 | n/a | $19,750.85M | -1.350 | n/a | $19,750.85M | -1.350 |
| LMP + toll + BESS Houston | 0 MW | $19,750.85M | -1.350 | 0 MW | $19,750.85M | -1.350 | 60 MW | $19,750.86M | -1.343 | 100 MW | $19,751.07M | -1.131 |
| LMP + BESS both | n/a | $19,749.77M | -2.431 | n/a | $19,749.77M | -2.431 | n/a | $19,749.77M | -2.431 | n/a | $19,749.77M | -2.431 |
| LMP + toll + BESS both | 0 MW | $19,749.77M | -2.431 | 0 MW | $19,749.77M | -2.431 | 60 MW | $19,749.78M | -2.425 | 100 MW | $19,749.99M | -2.213 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.620 | +0.319 | -3.024 | -2.164 |
| LMP + BESS Houston | -1.350 | +0.078 | -1.442 | -1.212 |
| LMP + BESS West | -1.082 | +0.094 | -1.238 | -0.934 |
| LMP + BESS both | -2.431 | +0.156 | -2.646 | -2.118 |
| LMP + toll + BESS Houston | -3.969 | +0.392 | -4.436 | -3.402 |
| LMP + toll + BESS West | -3.702 | +0.378 | -4.184 | -3.060 |
| LMP + toll + BESS both | -5.051 | +0.452 | -5.606 | -4.272 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,752.20M | $1.60M | $0.00M | $19,752.20M |
| 20 MW | $19,752.64M | $1.55M | $0.96M | $19,751.68M |
| 40 MW | $19,753.08M | $1.50M | $1.92M | $19,751.16M |
| 60 MW | $19,753.51M | $1.46M | $2.88M | $19,750.63M |
| 80 MW | $19,753.95M | $1.42M | $3.84M | $19,750.11M |
| 100 MW | $19,754.38M | $1.38M | $4.80M | $19,749.58M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.180 | 100 MW | +2.180 |
| $1.00 | $0.60M | +1.580 | 100 MW | +1.580 |
| $2.00 | $1.20M | +0.980 | 100 MW | +0.980 |
| $2.50 | $1.50M | +0.680 | 100 MW | +0.680 |
| $3.00 | $1.80M | +0.380 | 100 MW | +0.380 |
| $3.50 | $2.10M | +0.080 | 100 MW | +0.080 |
| $4.00 | $2.40M | -0.220 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.420 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.620 | 0 MW | +0.000 |
| $12.00 | $7.20M | -5.020 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,749.34M | -2.857 | 57,678 | $3.358M | 1.8% |
| intermediate (1500) | 1,500 | $19,749.56M | -2.641 | 71,240 | $4.137M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,749.58M | -2.620 | 73,147 | $4.245M | 0.7% |
| uncapped (None) | uncapped | $19,749.58M | -2.620 | 73,178 | $4.247M |  |

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
| HOUSTON | $-1.999M | $1.500M | $1.500M | $-1.500M | -0.499 |
| WEST | $-1.999M | $1.753M | $1.753M | $-1.247M | -0.753 |
