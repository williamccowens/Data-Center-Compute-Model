# Results tables — `run_n50_2026-05-24_ai_structural_mild`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,371.00M | $1.70M | $36,368.61M | $36,373.35M |
| 85d | $35,585.52M | $1.70M | $35,583.14M | $35,587.88M |
| 75d | $34,141.24M | $1.70M | $34,138.86M | $34,143.60M |
| 74d | $33,974.93M | $1.70M | $33,972.54M | $33,977.28M |
| 63d | $31,872.24M | $1.70M | $31,869.85M | $31,874.60M |
| 60d | $31,207.96M | $1.70M | $31,205.57M | $31,210.32M |
| 45d | $27,065.80M | $1.70M | $27,063.42M | $27,068.16M |
| 30d | $19,745.93M | $1.70M | $19,743.55M | $19,748.29M |
| 25d | $15,644.44M | $1.70M | $15,642.05M | $15,646.80M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,750.14M | $2.58M | $19,746.68M | $19,753.72M | +0.000 |
| LMP + BESS West | $19,749.13M | $2.47M | $19,745.77M | $19,752.53M | -1.015 |
| LMP + BESS Houston | $19,748.86M | $2.49M | $19,745.50M | $19,752.29M | -1.281 |
| LMP + toll | $19,748.23M | $1.89M | $19,745.65M | $19,750.83M | -1.915 |
| LMP + BESS both | $19,747.85M | $2.38M | $19,744.59M | $19,751.09M | -2.296 |
| LMP + toll + BESS West | $19,747.21M | $1.79M | $19,744.74M | $19,749.68M | -2.930 |
| LMP + toll + BESS Houston | $19,746.95M | $1.81M | $19,744.45M | $19,749.48M | -3.195 |
| LMP + toll + BESS both | $19,745.93M | $1.70M | $19,743.55M | $19,748.29M | -4.211 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $7.502M | $-4.617M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.213M | $0.989M | $-0.000M | $-0.000M | $-1.482M | $-3.000M |
| LMP + BESS West | $2.385M | $1.075M | $-0.000M | $-0.000M | $-1.476M | $-3.000M |
| LMP + BESS both | $5.020M | $1.642M | $-0.000M | $-0.000M | $-2.958M | $-6.000M |
| LMP + toll + BESS Houston | $2.929M | $7.775M | $-4.617M | $-4.800M | $-1.482M | $-3.000M |
| LMP + toll + BESS West | $2.380M | $8.583M | $-4.617M | $-4.800M | $-1.476M | $-3.000M |
| LMP + toll + BESS both | $5.633M | $8.532M | $-4.617M | $-4.800M | $-2.958M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$4.80 | Mean @ K=$4.80 | Δ vs LMP-only | MW @ K=$4.33 | Mean @ K=$4.33 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,750.14M ★ | +0.000 | n/a | $19,750.14M ★ | +0.000 | n/a | $19,750.14M | +0.000 | n/a | $19,750.14M | +0.000 |
| LMP + toll | 0 MW | $19,750.14M | +0.000 | 0 MW | $19,750.14M | +0.000 | 60 MW | $19,750.15M ★ | +0.008 | 100 MW | $19,750.43M ★ | +0.288 |
| LMP + BESS West | n/a | $19,749.13M | -1.015 | n/a | $19,749.13M | -1.015 | n/a | $19,749.13M | -1.015 | n/a | $19,749.13M | -1.015 |
| LMP + toll + BESS West | 0 MW | $19,749.13M | -1.015 | 0 MW | $19,749.13M | -1.015 | 60 MW | $19,749.14M | -1.007 | 100 MW | $19,749.42M | -0.727 |
| LMP + BESS Houston | n/a | $19,748.86M | -1.281 | n/a | $19,748.86M | -1.281 | n/a | $19,748.86M | -1.281 | n/a | $19,748.86M | -1.281 |
| LMP + toll + BESS Houston | 0 MW | $19,748.86M | -1.281 | 0 MW | $19,748.86M | -1.281 | 60 MW | $19,748.87M | -1.272 | 100 MW | $19,749.15M | -0.992 |
| LMP + BESS both | n/a | $19,747.85M | -2.296 | n/a | $19,747.85M | -2.296 | n/a | $19,747.85M | -2.296 | n/a | $19,747.85M | -2.296 |
| LMP + toll + BESS both | 0 MW | $19,747.85M | -2.296 | 0 MW | $19,747.85M | -2.296 | 60 MW | $19,747.86M | -2.287 | 100 MW | $19,748.14M | -2.007 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.915 | +0.785 | -2.899 | -0.740 |
| LMP + BESS Houston | -1.281 | +0.102 | -1.414 | -1.143 |
| LMP + BESS West | -1.015 | +0.118 | -1.208 | -0.873 |
| LMP + BESS both | -2.296 | +0.206 | -2.601 | -2.037 |
| LMP + toll + BESS Houston | -3.195 | +0.874 | -4.314 | -1.911 |
| LMP + toll + BESS West | -2.930 | +0.874 | -4.064 | -1.627 |
| LMP + toll + BESS both | -4.211 | +0.964 | -5.470 | -2.799 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,750.14M | $2.58M | $0.00M | $19,750.14M |
| 20 MW | $19,750.72M | $2.43M | $0.96M | $19,749.76M |
| 40 MW | $19,751.30M | $2.29M | $1.92M | $19,749.38M |
| 60 MW | $19,751.88M | $2.16M | $2.88M | $19,749.00M |
| 80 MW | $19,752.46M | $2.02M | $3.84M | $19,748.62M |
| 100 MW | $19,753.03M | $1.89M | $4.80M | $19,748.23M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.885 | 100 MW | +2.885 |
| $1.00 | $0.60M | +2.285 | 100 MW | +2.285 |
| $2.00 | $1.20M | +1.685 | 100 MW | +1.685 |
| $2.50 | $1.50M | +1.385 | 100 MW | +1.385 |
| $3.00 | $1.80M | +1.085 | 100 MW | +1.085 |
| $3.50 | $2.10M | +0.785 | 100 MW | +0.785 |
| $4.00 | $2.40M | +0.485 | 100 MW | +0.485 |
| $6.00 | $3.60M | -0.715 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.915 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.315 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,747.63M | -2.510 | 59,123 | $3.496M | 1.9% |
| intermediate (1500) | 1,500 | $19,748.07M | -2.069 | 74,089 | $4.403M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,748.22M | -1.927 | 76,926 | $4.603M | 0.8% |
| uncapped (None) | uncapped | $19,748.23M | -1.915 | 77,071 | $4.617M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.562M | $0.092M | $1.434M | $1.693M | $1.562M | $3.000M | $-1.438M |
| WEST | 4 | D | $1.813M | $0.113M | $1.626M | $1.969M | $1.813M | $3.000M | $-1.187M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.514M | $0.476M | $0.555M | $0.514M | $-2.486M |
| HOUSTON | 2 | D | $0.937M | $0.865M | $1.014M | $0.937M | $-2.063M |
| HOUSTON | 4 | D | $1.562M | $1.434M | $1.693M | $1.562M | $-1.438M |
| HOUSTON | 8 | D | $2.279M | $2.089M | $2.472M | $2.279M | $-0.721M |
| WEST | 1 | D | $0.589M | $0.531M | $0.636M | $0.589M | $-2.411M |
| WEST | 2 | D | $1.079M | $0.976M | $1.156M | $1.079M | $-1.921M |
| WEST | 4 | D | $1.813M | $1.626M | $1.969M | $1.813M | $-1.187M |
| WEST | 8 | D | $2.629M | $2.335M | $2.852M | $2.629M | $-0.371M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.969M | $1.562M | $1.562M | $-1.438M | -0.531 |
| WEST | $-1.969M | $1.813M | $1.813M | $-1.187M | -0.782 |
