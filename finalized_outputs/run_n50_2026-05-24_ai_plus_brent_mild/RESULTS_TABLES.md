# Results tables — `run_n50_2026-05-24_ai_plus_brent_mild`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,369.95M | $1.73M | $36,367.53M | $36,372.34M |
| 85d | $35,584.48M | $1.73M | $35,582.06M | $35,586.87M |
| 75d | $34,140.20M | $1.73M | $34,137.78M | $34,142.59M |
| 74d | $33,973.88M | $1.73M | $33,971.46M | $33,976.27M |
| 63d | $31,871.19M | $1.73M | $31,868.78M | $31,873.59M |
| 60d | $31,206.91M | $1.73M | $31,204.50M | $31,209.31M |
| 45d | $27,064.75M | $1.73M | $27,062.34M | $27,067.15M |
| 30d | $19,744.89M | $1.73M | $19,742.47M | $19,747.28M |
| 25d | $15,643.39M | $1.73M | $15,640.98M | $15,645.79M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,748.93M | $2.60M | $19,745.44M | $19,752.56M | +0.000 |
| LMP + BESS West | $19,747.97M | $2.50M | $19,744.58M | $19,751.42M | -0.960 |
| LMP + BESS Houston | $19,747.70M | $2.51M | $19,744.30M | $19,751.17M | -1.232 |
| LMP + toll | $19,747.08M | $1.92M | $19,744.44M | $19,749.72M | -1.850 |
| LMP + BESS both | $19,746.74M | $2.41M | $19,743.45M | $19,750.02M | -2.192 |
| LMP + toll + BESS West | $19,746.12M | $1.82M | $19,743.61M | $19,748.62M | -2.810 |
| LMP + toll + BESS Houston | $19,745.85M | $1.83M | $19,743.28M | $19,748.41M | -3.082 |
| LMP + toll + BESS both | $19,744.89M | $1.73M | $19,742.47M | $19,747.28M | -4.042 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $7.697M | $-4.747M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.286M | $1.007M | $-0.000M | $-0.000M | $-1.524M | $-3.000M |
| LMP + BESS West | $2.459M | $1.118M | $-0.000M | $-0.000M | $-1.537M | $-3.000M |
| LMP + BESS both | $5.162M | $1.708M | $-0.000M | $-0.000M | $-3.062M | $-6.000M |
| LMP + toll + BESS Houston | $3.015M | $7.975M | $-4.747M | $-4.800M | $-1.524M | $-3.000M |
| LMP + toll + BESS West | $2.458M | $8.816M | $-4.747M | $-4.800M | $-1.537M | $-3.000M |
| LMP + toll + BESS both | $5.786M | $8.781M | $-4.747M | $-4.800M | $-3.062M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$4.91 | Mean @ K=$4.91 | Δ vs LMP-only | MW @ K=$4.42 | Mean @ K=$4.42 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,748.93M ★ | +0.000 | n/a | $19,748.93M ★ | +0.000 | n/a | $19,748.93M | +0.000 | n/a | $19,748.93M | +0.000 |
| LMP + toll | 0 MW | $19,748.93M | +0.000 | 0 MW | $19,748.93M | +0.000 | 60 MW | $19,748.94M ★ | +0.008 | 100 MW | $19,749.22M ★ | +0.295 |
| LMP + BESS West | n/a | $19,747.97M | -0.960 | n/a | $19,747.97M | -0.960 | n/a | $19,747.97M | -0.960 | n/a | $19,747.97M | -0.960 |
| LMP + toll + BESS West | 0 MW | $19,747.97M | -0.960 | 0 MW | $19,747.97M | -0.960 | 60 MW | $19,747.98M | -0.952 | 100 MW | $19,748.26M | -0.665 |
| LMP + BESS Houston | n/a | $19,747.70M | -1.232 | n/a | $19,747.70M | -1.232 | n/a | $19,747.70M | -1.232 | n/a | $19,747.70M | -1.232 |
| LMP + toll + BESS Houston | 0 MW | $19,747.70M | -1.232 | 0 MW | $19,747.70M | -1.232 | 60 MW | $19,747.70M | -1.223 | 100 MW | $19,747.99M | -0.937 |
| LMP + BESS both | n/a | $19,746.74M | -2.192 | n/a | $19,746.74M | -2.192 | n/a | $19,746.74M | -2.192 | n/a | $19,746.74M | -2.192 |
| LMP + toll + BESS both | 0 MW | $19,746.74M | -2.192 | 0 MW | $19,746.74M | -2.192 | 60 MW | $19,746.74M | -2.183 | 100 MW | $19,747.03M | -1.897 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.850 | +0.788 | -2.844 | -0.664 |
| LMP + BESS Houston | -1.232 | +0.103 | -1.367 | -1.093 |
| LMP + BESS West | -0.960 | +0.120 | -1.157 | -0.816 |
| LMP + BESS both | -2.192 | +0.209 | -2.502 | -1.931 |
| LMP + toll + BESS Houston | -3.082 | +0.878 | -4.211 | -1.786 |
| LMP + toll + BESS West | -2.810 | +0.878 | -3.955 | -1.496 |
| LMP + toll + BESS both | -4.042 | +0.969 | -5.314 | -2.618 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,748.93M | $2.60M | $0.00M | $19,748.93M |
| 20 MW | $19,749.52M | $2.46M | $0.96M | $19,748.56M |
| 40 MW | $19,750.11M | $2.32M | $1.92M | $19,748.19M |
| 60 MW | $19,750.70M | $2.18M | $2.88M | $19,747.82M |
| 80 MW | $19,751.29M | $2.05M | $3.84M | $19,747.45M |
| 100 MW | $19,751.88M | $1.92M | $4.80M | $19,747.08M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.950 | 100 MW | +2.950 |
| $1.00 | $0.60M | +2.350 | 100 MW | +2.350 |
| $2.00 | $1.20M | +1.750 | 100 MW | +1.750 |
| $2.50 | $1.50M | +1.450 | 100 MW | +1.450 |
| $3.00 | $1.80M | +1.150 | 100 MW | +1.150 |
| $3.50 | $2.10M | +0.850 | 100 MW | +0.850 |
| $4.00 | $2.40M | +0.550 | 100 MW | +0.550 |
| $6.00 | $3.60M | -0.650 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.850 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.250 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,746.47M | -2.453 | 59,095 | $3.597M | 1.9% |
| intermediate (1500) | 1,500 | $19,746.92M | -2.004 | 74,072 | $4.528M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,747.07M | -1.862 | 76,926 | $4.733M | 0.8% |
| uncapped (None) | uncapped | $19,747.08M | -1.850 | 77,071 | $4.747M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.606M | $0.093M | $1.477M | $1.739M | $1.606M | $3.000M | $-1.394M |
| WEST | 4 | D | $1.865M | $0.115M | $1.674M | $2.025M | $1.865M | $3.000M | $-1.135M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.529M | $0.490M | $0.570M | $0.529M | $-2.471M |
| HOUSTON | 2 | D | $0.964M | $0.890M | $1.042M | $0.964M | $-2.036M |
| HOUSTON | 4 | D | $1.606M | $1.477M | $1.739M | $1.606M | $-1.394M |
| HOUSTON | 8 | D | $2.343M | $2.152M | $2.540M | $2.343M | $-0.657M |
| WEST | 1 | D | $0.605M | $0.547M | $0.654M | $0.605M | $-2.395M |
| WEST | 2 | D | $1.110M | $1.005M | $1.188M | $1.110M | $-1.890M |
| WEST | 4 | D | $1.865M | $1.674M | $2.025M | $1.865M | $-1.135M |
| WEST | 8 | D | $2.704M | $2.404M | $2.933M | $2.704M | $-0.296M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.950M | $1.606M | $1.606M | $-1.394M | -0.556 |
| WEST | $-1.950M | $1.865M | $1.865M | $-1.135M | -0.815 |
