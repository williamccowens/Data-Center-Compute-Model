# Results tables — `run_n50_2026-05-24_mild_drift`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,371.69M | $1.26M | $36,369.62M | $36,373.28M |
| 85d | $35,586.21M | $1.26M | $35,584.15M | $35,587.80M |
| 75d | $34,141.93M | $1.26M | $34,139.87M | $34,143.52M |
| 74d | $33,975.62M | $1.26M | $33,973.55M | $33,977.21M |
| 63d | $31,872.93M | $1.26M | $31,870.86M | $31,874.52M |
| 60d | $31,208.65M | $1.26M | $31,206.58M | $31,210.24M |
| 45d | $27,066.49M | $1.26M | $27,064.42M | $27,068.08M |
| 30d | $19,746.62M | $1.26M | $19,744.55M | $19,748.21M |
| 25d | $15,645.13M | $1.26M | $15,643.06M | $15,646.72M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,751.59M | $1.62M | $19,748.95M | $19,753.61M | +0.000 |
| LMP + BESS West | $19,750.54M | $1.54M | $19,748.03M | $19,752.43M | -1.054 |
| LMP + BESS Houston | $19,750.26M | $1.56M | $19,747.73M | $19,752.19M | -1.325 |
| LMP + BESS both | $19,749.21M | $1.48M | $19,746.81M | $19,751.01M | -2.379 |
| LMP + toll | $19,749.00M | $1.40M | $19,746.69M | $19,750.72M | -2.587 |
| LMP + toll + BESS West | $19,747.95M | $1.32M | $19,745.77M | $19,749.59M | -3.641 |
| LMP + toll + BESS Houston | $19,747.68M | $1.34M | $19,745.48M | $19,749.34M | -3.912 |
| LMP + toll + BESS both | $19,746.62M | $1.26M | $19,744.55M | $19,748.21M | -4.966 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $6.525M | $-4.312M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.097M | $0.952M | $-0.000M | $-0.000M | $-1.373M | $-3.000M |
| LMP + BESS West | $2.255M | $1.059M | $-0.000M | $-0.000M | $-1.369M | $-3.000M |
| LMP + BESS both | $4.763M | $1.600M | $-0.000M | $-0.000M | $-2.742M | $-6.000M |
| LMP + toll + BESS Houston | $2.770M | $6.803M | $-4.312M | $-4.800M | $-1.373M | $-3.000M |
| LMP + toll + BESS West | $2.250M | $7.589M | $-4.312M | $-4.800M | $-1.369M | $-3.000M |
| LMP + toll + BESS both | $5.332M | $7.556M | $-4.312M | $-4.800M | $-2.742M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only | MW @ K=$3.68 | Mean @ K=$3.68 | Δ vs LMP-only | MW @ K=$3.32 | Mean @ K=$3.32 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,751.59M ★ | +0.000 | n/a | $19,751.59M ★ | +0.000 | n/a | $19,751.59M | +0.000 | n/a | $19,751.59M | +0.000 |
| LMP + toll | 0 MW | $19,751.59M | +0.000 | 0 MW | $19,751.59M | +0.000 | 60 MW | $19,751.60M ★ | +0.007 | 100 MW | $19,751.81M ★ | +0.221 |
| LMP + BESS West | n/a | $19,750.54M | -1.054 | n/a | $19,750.54M | -1.054 | n/a | $19,750.54M | -1.054 | n/a | $19,750.54M | -1.054 |
| LMP + toll + BESS West | 0 MW | $19,750.54M | -1.054 | 0 MW | $19,750.54M | -1.054 | 60 MW | $19,750.54M | -1.047 | 100 MW | $19,750.76M | -0.833 |
| LMP + BESS Houston | n/a | $19,750.26M | -1.325 | n/a | $19,750.26M | -1.325 | n/a | $19,750.26M | -1.325 | n/a | $19,750.26M | -1.325 |
| LMP + toll + BESS Houston | 0 MW | $19,750.26M | -1.325 | 0 MW | $19,750.26M | -1.325 | 60 MW | $19,750.27M | -1.318 | 100 MW | $19,750.49M | -1.104 |
| LMP + BESS both | n/a | $19,749.21M | -2.379 | n/a | $19,749.21M | -2.379 | n/a | $19,749.21M | -2.379 | n/a | $19,749.21M | -2.379 |
| LMP + toll + BESS both | 0 MW | $19,749.21M | -2.379 | 0 MW | $19,749.21M | -2.379 | 60 MW | $19,749.22M | -2.372 | 100 MW | $19,749.43M | -2.158 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -2.587 | +0.323 | -2.997 | -2.124 |
| LMP + BESS Houston | -1.325 | +0.079 | -1.419 | -1.185 |
| LMP + BESS West | -1.054 | +0.095 | -1.213 | -0.904 |
| LMP + BESS both | -2.379 | +0.158 | -2.597 | -2.061 |
| LMP + toll + BESS Houston | -3.912 | +0.397 | -4.385 | -3.336 |
| LMP + toll + BESS West | -3.641 | +0.383 | -4.131 | -2.990 |
| LMP + toll + BESS both | -4.966 | +0.458 | -5.529 | -4.176 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,751.59M | $1.62M | $0.00M | $19,751.59M |
| 20 MW | $19,752.03M | $1.57M | $0.96M | $19,751.07M |
| 40 MW | $19,752.48M | $1.53M | $1.92M | $19,750.56M |
| 60 MW | $19,752.92M | $1.48M | $2.88M | $19,750.04M |
| 80 MW | $19,753.36M | $1.44M | $3.84M | $19,749.52M |
| 100 MW | $19,753.80M | $1.40M | $4.80M | $19,749.00M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +2.213 | 100 MW | +2.213 |
| $1.00 | $0.60M | +1.613 | 100 MW | +1.613 |
| $2.00 | $1.20M | +1.013 | 100 MW | +1.013 |
| $2.50 | $1.50M | +0.713 | 100 MW | +0.713 |
| $3.00 | $1.80M | +0.413 | 100 MW | +0.413 |
| $3.50 | $2.10M | +0.113 | 100 MW | +0.113 |
| $4.00 | $2.40M | -0.187 | 0 MW | +0.000 |
| $6.00 | $3.60M | -1.387 | 0 MW | +0.000 |
| $8.00 | $4.80M | -2.587 | 0 MW | +0.000 |
| $12.00 | $7.20M | -4.987 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,748.76M | -2.828 | 57,680 | $3.409M | 1.8% |
| intermediate (1500) | 1,500 | $19,748.98M | -2.608 | 71,249 | $4.200M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,749.00M | -2.587 | 73,164 | $4.310M | 0.7% |
| uncapped (None) | uncapped | $19,749.00M | -2.587 | 73,194 | $4.312M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.522M | $0.075M | $1.428M | $1.643M | $1.522M | $3.000M | $-1.478M |
| WEST | 4 | D | $1.780M | $0.094M | $1.615M | $1.922M | $1.780M | $3.000M | $-1.220M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.503M | $0.473M | $0.548M | $0.503M | $-2.497M |
| HOUSTON | 2 | D | $0.917M | $0.857M | $0.992M | $0.917M | $-2.083M |
| HOUSTON | 4 | D | $1.522M | $1.428M | $1.643M | $1.522M | $-1.478M |
| HOUSTON | 8 | D | $2.213M | $2.074M | $2.396M | $2.213M | $-0.787M |
| WEST | 1 | D | $0.580M | $0.526M | $0.631M | $0.580M | $-2.420M |
| WEST | 2 | D | $1.062M | $0.965M | $1.153M | $1.062M | $-1.938M |
| WEST | 4 | D | $1.780M | $1.615M | $1.922M | $1.780M | $-1.220M |
| WEST | 8 | D | $2.571M | $2.320M | $2.776M | $2.571M | $-0.429M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.990M | $1.522M | $1.522M | $-1.478M | -0.512 |
| WEST | $-1.990M | $1.780M | $1.780M | $-1.220M | -0.769 |
