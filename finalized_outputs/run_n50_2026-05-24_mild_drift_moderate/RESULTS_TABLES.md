# Results tables — `run_n50_2026-05-24_mild_drift_moderate`

Auto-generated from the sweep / MC CSVs in this folder by `model/render_tables.py`. For a downloadable version that pastes cleanly into Word or Google Docs, use [`RESULTS_TABLES.html`](./RESULTS_TABLES.html).

---

### Cadence profit  ([`mc_summary_n50_doc_blended.csv`](./mc_summary_n50_doc_blended.csv))

Per-cadence mean profit across 50 MC paths. Winner marked with ★.

| Cadence | Mean | Std | p05 | p95 |
|:---|---:|---:|---:|---:|
| 90d ★ | $36,370.14M | $3.83M | $36,361.84M | $36,373.28M |
| 85d | $35,584.67M | $3.83M | $35,576.37M | $35,587.80M |
| 75d | $34,140.39M | $3.83M | $34,132.09M | $34,143.52M |
| 74d | $33,974.07M | $3.83M | $33,965.77M | $33,977.21M |
| 63d | $31,871.38M | $3.83M | $31,863.09M | $31,874.52M |
| 60d | $31,207.10M | $3.83M | $31,198.81M | $31,210.24M |
| 45d | $27,064.94M | $3.83M | $27,056.65M | $27,068.08M |
| 30d | $19,745.07M | $3.83M | $19,736.78M | $19,748.21M |
| 25d | $15,643.58M | $3.83M | $15,635.29M | $15,646.72M |

---

### Procurement scenarios — profit  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

8-scenario profit comparison at the locked cadence (50 MC paths). Winner marked with ★.

| Scenario | Mean | Std | p05 | p95 | Δ vs LMP-only ($M) |
|:---|---:|---:|---:|---:|---:|
| LMP only ★ | $19,748.39M | $7.39M | $19,731.88M | $19,753.61M | +0.000 |
| LMP + BESS West | $19,747.49M | $7.04M | $19,731.69M | $19,752.43M | -0.899 |
| LMP + BESS Houston | $19,747.21M | $7.05M | $19,731.50M | $19,752.19M | -1.175 |
| LMP + toll | $19,747.15M | $4.52M | $19,737.35M | $19,750.72M | -1.239 |
| LMP + BESS both | $19,746.31M | $6.70M | $19,731.31M | $19,751.01M | -2.074 |
| LMP + toll + BESS West | $19,746.25M | $4.17M | $19,737.16M | $19,749.59M | -2.139 |
| LMP + toll + BESS Houston | $19,745.97M | $4.18M | $19,736.97M | $19,749.34M | -2.414 |
| LMP + toll + BESS both | $19,745.07M | $3.83M | $19,736.78M | $19,748.21M | -3.313 |

---

### Procurement scenarios — cost / revenue components  ([`power_procurement_mc_n50_doc_blended_c30.csv`](./power_procurement_mc_n50_doc_blended_c30.csv))

Component contributions in $M, signs chosen so positive = adds to profit.

| Scenario | BESS rev | LMP cost saved | Toll cost | Toll lease | BESS charge | BESS lease |
|:---|---:|---:|---:|---:|---:|---:|
| LMP only | $0.000M | $0.000M | $-0.000M | $-0.000M | $-0.000M | $-0.000M |
| LMP + toll | $0.000M | $8.204M | $-4.644M | $-4.800M | $-0.000M | $-0.000M |
| LMP + BESS Houston | $2.377M | $1.025M | $-0.000M | $-0.000M | $-1.577M | $-3.000M |
| LMP + BESS West | $2.497M | $1.177M | $-0.000M | $-0.000M | $-1.573M | $-3.000M |
| LMP + BESS both | $5.327M | $1.750M | $-0.000M | $-0.000M | $-3.150M | $-6.000M |
| LMP + toll + BESS Houston | $3.125M | $8.482M | $-4.644M | $-4.800M | $-1.577M | $-3.000M |
| LMP + toll + BESS West | $2.519M | $9.360M | $-4.644M | $-4.800M | $-1.573M | $-3.000M |
| LMP + toll + BESS both | $5.964M | $9.316M | $-4.644M | $-4.800M | $-3.150M | $-6.000M |

---

### Phase C at three capacity-payment rates (rational MW commitment)  ([`phase_c_multi_k_n50_doc_blended_c30.csv`](./phase_c_multi_k_n50_doc_blended_c30.csv))

8 procurement scenarios × 3 capacity-payment rates ($/kW-mo): the seller-side $8, the per-snapshot sub-breakeven 0.9 × K*, and a $5 lower-estimate. For each (scenario × K) cell, MW = 100 if committing to the full toll reservation beats walking away at that K, else MW = 0 (the toll row collapses to its non-toll twin's profit). Winner per K marked with ★.

| Scenario | MW @ K=$8.00 | Mean @ K=$8.00 | Δ vs LMP-only | MW @ K=$5.93 | Mean @ K=$5.93 | Δ vs LMP-only | MW @ K=$5.34 | Mean @ K=$5.34 | Δ vs LMP-only | MW @ K=$5.00 | Mean @ K=$5.00 | Δ vs LMP-only |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LMP only | n/a | $19,748.39M ★ | +0.000 | n/a | $19,748.39M | +0.000 | n/a | $19,748.39M | +0.000 | n/a | $19,748.39M | +0.000 |
| LMP + toll | 0 MW | $19,748.39M | +0.000 | 60 MW | $19,748.40M ★ | +0.010 | 100 MW | $19,748.74M ★ | +0.356 | 100 MW | $19,748.95M ★ | +0.561 |
| LMP + BESS West | n/a | $19,747.49M | -0.899 | n/a | $19,747.49M | -0.899 | n/a | $19,747.49M | -0.899 | n/a | $19,747.49M | -0.899 |
| LMP + toll + BESS West | 0 MW | $19,747.49M | -0.899 | 60 MW | $19,747.50M | -0.889 | 100 MW | $19,747.84M | -0.543 | 100 MW | $19,748.05M | -0.339 |
| LMP + BESS Houston | n/a | $19,747.21M | -1.175 | n/a | $19,747.21M | -1.175 | n/a | $19,747.21M | -1.175 | n/a | $19,747.21M | -1.175 |
| LMP + toll + BESS Houston | 0 MW | $19,747.21M | -1.175 | 60 MW | $19,747.22M | -1.164 | 100 MW | $19,747.57M | -0.818 | 100 MW | $19,747.77M | -0.614 |
| LMP + BESS both | n/a | $19,746.31M | -2.074 | n/a | $19,746.31M | -2.074 | n/a | $19,746.31M | -2.074 | n/a | $19,746.31M | -2.074 |
| LMP + toll + BESS both | 0 MW | $19,746.31M | -2.074 | 60 MW | $19,746.32M | -2.064 | 100 MW | $19,746.67M | -1.718 | 100 MW | $19,746.87M | -1.513 |

---

### Procurement scenarios — paired Δprofit vs LMP-only  ([`power_procurement_deltas_n50_doc_blended.csv`](./power_procurement_deltas_n50_doc_blended.csv))

Per-path paired delta vs the LMP-only baseline ($M). Same MC paths, so this is a cleaner Δ than subtracting the marginal means above.

| Scenario | Δ mean | Δ std | Δ p05 | Δ p95 |
|:---|---:|---:|---:|---:|
| LMP only | +0.000 | +0.000 | +0.000 | +0.000 |
| LMP + toll | -1.239 | +2.955 | -2.997 | +5.470 |
| LMP + BESS Houston | -1.175 | +0.351 | -1.410 | -0.375 |
| LMP + BESS West | -0.899 | +0.357 | -1.213 | -0.129 |
| LMP + BESS both | -2.074 | +0.703 | -2.597 | -0.532 |
| LMP + toll + BESS Houston | -2.414 | +3.300 | -4.385 | +5.088 |
| LMP + toll + BESS West | -2.139 | +3.302 | -4.131 | +5.234 |
| LMP + toll + BESS both | -3.313 | +3.647 | -5.529 | +4.857 |

---

### Reservation-MW sweep  ([`reservation_sweep_n50_doc_blended_c30.csv`](./reservation_sweep_n50_doc_blended_c30.csv))

Buyer-side decision: how much Houston toll MW to commit ex ante, before MC paths realize. Net = base profit − lease at default $8/kW-mo. ★ marks the best.

| MW reserved | Base profit (excl. lease) | Base std | Lease @ $8/kW-mo | Net |
|:---|---:|---:|---:|---:|
| 0 MW ★ | $19,748.39M | $7.39M | $0.00M | $19,748.39M |
| 20 MW | $19,749.10M | $6.81M | $0.96M | $19,748.14M |
| 40 MW | $19,749.82M | $6.23M | $1.92M | $19,747.90M |
| 60 MW | $19,750.53M | $5.65M | $2.88M | $19,747.65M |
| 80 MW | $19,751.24M | $5.08M | $3.84M | $19,747.40M |
| 100 MW | $19,751.95M | $4.52M | $4.80M | $19,747.15M |

---

### Capacity-payment sweep  ([`capacity_payment_sweep_n50_doc_blended_c30.csv`](./capacity_payment_sweep_n50_doc_blended_c30.csv))

Seller-side rate sensitivity. The 'optimal MW' column is the buyer's best response from the reservation sweep. Breakeven K* is where Δ (fixed 100 MW) crosses zero.

| K ($/kW-mo) | Lease @ 100 MW | Δ (fixed 100 MW) vs LMP-only | Optimal MW | Δ (optimal) vs LMP-only |
|:---|---:|---:|---:|---:|
| $0.00 | $0.00M | +3.561 | 100 MW | +3.561 |
| $1.00 | $0.60M | +2.961 | 100 MW | +2.961 |
| $2.00 | $1.20M | +2.361 | 100 MW | +2.361 |
| $2.50 | $1.50M | +2.061 | 100 MW | +2.061 |
| $3.00 | $1.80M | +1.761 | 100 MW | +1.761 |
| $3.50 | $2.10M | +1.461 | 100 MW | +1.461 |
| $4.00 | $2.40M | +1.161 | 100 MW | +1.161 |
| $6.00 | $3.60M | -0.039 | 0 MW | +0.000 |
| $8.00 | $4.80M | -1.239 | 0 MW | +0.000 |
| $12.00 | $7.20M | -3.639 | 0 MW | +0.000 |

---

### Toll daily-cap sweep  ([`toll_cap_sweep_n50_doc_blended_c30.csv`](./toll_cap_sweep_n50_doc_blended_c30.csv))

4-bracket sensitivity to the SCGT daily-output cap. 'Hours binding' = fraction of LP hours where the cap was active.

| Bracket | Cap (MWh/day) | Mean profit | Δ vs LMP-only | Toll MWh dispatched | Toll cost | Hours binding |
|:---|---:|---:|---:|---:|---:|---:|
| peaker (720) | 720 | $19,746.19M | -2.193 | 58,116 | $3.514M | 1.8% |
| intermediate (1500) | 1,500 | $19,746.86M | -1.531 | 72,223 | $4.416M | 1.1% |
| near-nameplate (2280) | 2,280 | $19,747.13M | -1.262 | 74,614 | $4.628M | 0.7% |
| uncapped (None) | uncapped | $19,747.15M | -1.239 | 74,710 | $4.644M |  |

---

### TBx swap valuation (primary x)  ([`tbx_swap_primary_n50.csv`](./tbx_swap_primary_n50.csv))

Virtual BESS via TBx swap at the primary spread multiplier. Breakeven = expected floating leg; net = floating mean − fixed payment, both quoted against the $3M/site/6-mo physical lease so the head-to-head is direct.

| Site | x | Settlement | E[floating] | Std | p05 | p95 | Breakeven fixed | Fixed payment | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|
| HOUSTON | 4 | D | $1.634M | $0.267M | $1.439M | $2.278M | $1.634M | $3.000M | $-1.366M |
| WEST | 4 | D | $1.893M | $0.277M | $1.615M | $2.524M | $1.893M | $3.000M | $-1.107M |

---

### TBx x-sensitivity  ([`tbx_swap_xsweep_n50.csv`](./tbx_swap_xsweep_n50.csv))

Floating-leg value at x ∈ {1, 2, 4, 8} per site.

| Site | x | Settlement | E[floating] | p05 | p95 | Breakeven fixed | Net @ phys lease |
|:---|---:|:---|---:|---:|---:|---:|---:|
| HOUSTON | 1 | D | $0.536M | $0.478M | $0.714M | $0.536M | $-2.464M |
| HOUSTON | 2 | D | $0.979M | $0.867M | $1.325M | $0.979M | $-2.021M |
| HOUSTON | 4 | D | $1.634M | $1.439M | $2.278M | $1.634M | $-1.366M |
| HOUSTON | 8 | D | $2.388M | $2.089M | $3.366M | $2.388M | $-0.612M |
| WEST | 1 | D | $0.613M | $0.526M | $0.797M | $0.613M | $-2.387M |
| WEST | 2 | D | $1.125M | $0.965M | $1.477M | $1.125M | $-1.875M |
| WEST | 4 | D | $1.893M | $1.615M | $2.524M | $1.893M | $-1.107M |
| WEST | 8 | D | $2.750M | $2.320M | $3.694M | $2.750M | $-0.250M |

---

### Physical vs virtual BESS  ([`phys_vs_virt_bess_n50.csv`](./phys_vs_virt_bess_n50.csv))

LP-dispatched physical BESS vs TBx-swap virtual BESS, both net of $3M/site/6-mo lease where applicable.

| Site | Physical net | Virtual floating | Virtual breakeven | Virtual net @ $3M | Phys − Virt |
|:---|---:|---:|---:|---:|---:|
| HOUSTON | $-1.912M | $1.634M | $1.634M | $-1.366M | -0.545 |
| WEST | $-1.912M | $1.893M | $1.893M | $-1.107M | -0.805 |
