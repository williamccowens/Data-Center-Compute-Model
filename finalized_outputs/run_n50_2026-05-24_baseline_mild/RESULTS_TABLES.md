# Results tables — `run_n50_2026-05-24_baseline_mild`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,371.31M | $1.70M | $36,368.93M | $36,373.66M |
| 85d | $35,585.84M | $1.70M | $35,583.46M | $35,588.19M |
| 75d | $34,141.56M | $1.70M | $34,139.18M | $34,143.91M |
| 74d | $33,975.24M | $1.70M | $33,972.86M | $33,977.59M |
| 63d | $31,872.56M | $1.70M | $31,870.18M | $31,874.91M |
| 60d | $31,208.28M | $1.70M | $31,205.90M | $31,210.63M |
| 45d | $27,066.12M | $1.70M | $27,063.74M | $27,068.47M |
| 30d | $19,746.25M | $1.70M | $19,743.87M | $19,748.60M |
| 25d | $15,644.76M | $1.70M | $15,642.38M | $15,647.11M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,750.55M | $2.57M | $19,747.10M | $19,754.11M | +0.000 |
| LMP + BESS West | $19,749.52M | $2.46M | $19,746.17M | $19,752.90M | -1.033 |
| LMP + BESS Houston | $19,749.25M | $2.48M | $19,745.90M | $19,752.67M | -1.297 |
| LMP + toll | $19,748.58M | $1.89M | $19,746.01M | $19,751.17M | -1.969 |
| LMP + BESS both | $19,748.22M | $2.38M | $19,744.97M | $19,751.45M | -2.330 |
| LMP + toll + BESS West | $19,747.55M | $1.78M | $19,745.08M | $19,750.00M | -3.003 |
| LMP + toll + BESS Houston | $19,747.28M | $1.80M | $19,744.80M | $19,749.80M | -3.266 |
| LMP + toll + BESS both | $19,746.25M | $1.70M | $19,743.87M | $19,748.60M | -4.299 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $7.365M | $-4.534M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.199M | $0.972M | $-0.000M | $-0.000M | $-1.468M | $-3.000M |
| LMP + BESS West | $2.340M | $1.082M | $-0.000M | $-0.000M | $-1.455M | $-3.000M |
| LMP + BESS both | $4.958M | $1.636M | $-0.000M | $-0.000M | $-2.924M | $-6.000M |
| LMP + toll + BESS Houston | $2.901M | $7.636M | $-4.534M | $-4.800M | $-1.468M | $-3.000M |
| LMP + toll + BESS West | $2.350M | $8.437M | $-4.534M | $-4.800M | $-1.455M | $-3.000M |
| LMP + toll + BESS both | $5.553M | $8.406M | $-4.534M | $-4.800M | $-2.924M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$4.71 | Mean @ K=$4.71 | Δ vs LMP-only | MW @ K=$4.25 | Mean @ K=$4.25 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,750.55M ★ | +0.000 | n/a | $19,750.55M ★ | +0.000 | n/a | $19,750.55M | +0.000 | n/a | $19,750.55M | +0.000 |
| LMP + toll | 0 MW | $19,750.55M | +0.000 | 0 MW | $19,750.55M | +0.000 | 60 MW | $19,750.56M ★ | +0.008 | 100 MW | $19,750.83M ★ | +0.283 |
| LMP + BESS West | n/a | $19,749.52M | -1.033 | n/a | $19,749.52M | -1.033 | n/a | $19,749.52M | -1.033 | n/a | $19,749.52M | -1.033 |
| LMP + toll + BESS West | 0 MW | $19,749.52M | -1.033 | 0 MW | $19,749.52M | -1.033 | 60 MW | $19,749.52M | -1.025 | 100 MW | $19,749.80M | -0.750 |
| LMP + BESS Houston | n/a | $19,749.25M | -1.297 | n/a | $19,749.25M | -1.297 | n/a | $19,749.25M | -1.297 | n/a | $19,749.25M | -1.297 |
| LMP + toll + BESS Houston | 0 MW | $19,749.25M | -1.297 | 0 MW | $19,749.25M | -1.297 | 60 MW | $19,749.26M | -1.289 | 100 MW | $19,749.54M | -1.014 |
| LMP + BESS both | n/a | $19,748.22M | -2.330 | n/a | $19,748.22M | -2.330 | n/a | $19,748.22M | -2.330 | n/a | $19,748.22M | -2.330 |
| LMP + toll + BESS both | 0 MW | $19,748.22M | -2.330 | 0 MW | $19,748.22M | -2.330 | 60 MW | $19,748.23M | -2.322 | 100 MW | $19,748.50M | -2.047 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.969 | +0.783 | -2.947 | -0.799 |
| LMP + BESS Houston | -1.297 | +0.101 | -1.430 | -1.161 |
| LMP + BESS West | -1.033 | +0.117 | -1.225 | -0.891 |
| LMP + BESS both | -2.330 | +0.205 | -2.634 | -2.072 |
| LMP + toll + BESS Houston | -3.266 | +0.871 | -4.377 | -1.987 |
| LMP + toll + BESS West | -3.003 | +0.872 | -4.129 | -1.705 |
| LMP + toll + BESS both | -4.299 | +0.961 | -5.550 | -2.893 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,750.55M | $2.57M | $0.00M | $19,750.55M |
| 20 MW | $19,751.12M | $2.43M | $0.96M | $19,750.16M |
| 40 MW | $19,751.69M | $2.29M | $1.92M | $19,749.77M |
| 60 MW | $19,752.25M | $2.15M | $2.88M | $19,749.37M |
| 80 MW | $19,752.82M | $2.02M | $3.84M | $19,748.98M |
| 100 MW | $19,753.38M | $1.89M | $4.80M | $19,748.58M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.831 | 100 MW | +2.831 |
| $1.00 | $0.60M | +2.231 | 100 MW | +2.231 |
| $2.00 | $1.20M | +1.631 | 100 MW | +1.631 |
| $2.50 | $1.50M | +1.331 | 100 MW | +1.331 |
| $3.00 | $1.80M | +1.031 | 100 MW | +1.031 |
| $3.50 | $2.10M | +0.731 | 100 MW | +0.731 |
| $4.00 | $2.40M | +0.431 | 100 MW | +0.431 |
| $6.00 | $3.60M | -0.769 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.969 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.369 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,747.99M | -2.555 | 58,354 | $3.442M | 1.8% |
| intermediate (1500) | 1,500 | $19,748.43M | -2.122 | 72,946 | $4.325M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,748.57M | -1.981 | 75,700 | $4.521M | 0.8% |
| uncapped (None) | uncapped | $19,748.58M | -1.969 | 75,844 | $4.534M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.547M | $0.091M | $1.420M | $1.678M | $1.547M | $3.000M | $-1.453M |
| WEST | 4 | D | $1.796M | $0.112M | $1.610M | $1.950M | $1.796M | $3.000M | $-1.204M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.509M | $0.471M | $0.550M | $0.509M | $-2.491M |
| HOUSTON | 2 | D | $0.928M | $0.856M | $1.005M | $0.928M | $-2.072M |
| HOUSTON | 4 | D | $1.547M | $1.420M | $1.678M | $1.547M | $-1.453M |
| HOUSTON | 8 | D | $2.257M | $2.069M | $2.450M | $2.257M | $-0.743M |
| WEST | 1 | D | $0.583M | $0.526M | $0.630M | $0.583M | $-2.417M |
| WEST | 2 | D | $1.069M | $0.966M | $1.145M | $1.069M | $-1.931M |
| WEST | 4 | D | $1.796M | $1.610M | $1.950M | $1.796M | $-1.204M |
| WEST | 8 | D | $2.604M | $2.312M | $2.825M | $2.604M | $-0.396M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.983M | $1.547M | $1.547M | $-1.453M | -0.530 |
| WEST | $-1.983M | $1.796M | $1.796M | $-1.204M | -0.779 |
