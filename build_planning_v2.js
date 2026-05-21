// Generates "Final Project Current Status Report.docx" — fills out the planning sections
// (Training+Inference, Inference, Conversion, Power, Model Dynamic) with
// concrete descriptions of what's actually implemented in code. Leaves
// the class-report skeleton (Executive Summary, Model Setup, etc.) blank
// because the user is writing that themselves.

const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageBreak, ExternalHyperlink,
} = require("docx");

// Write the generated docx next to this script (= repo root where the
// tracked "Final Project Current Status Report.docx" lives). Previously
// hard-coded to a Desktop path that no longer exists.
const ROOT = __dirname;

// ── Style helpers ────────────────────────────────────────────────────
const P = (text, opts = {}) => new Paragraph({
  children: [new TextRun({ text, ...opts })],
  spacing: { after: 120 },
});
const PR = (...runs) => new Paragraph({
  children: runs.map(r =>
    typeof r === "string" ? new TextRun(r) : new TextRun(r)),
  spacing: { after: 120 },
});
const H1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, bold: true })],
});
const H2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, bold: true })],
});
const H3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, bold: true })],
});
const BULLET = (text) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun(text)],
  spacing: { after: 80 },
});
const BULLET_R = (...runs) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: runs.map(r =>
    typeof r === "string" ? new TextRun(r) : new TextRun(r)),
  spacing: { after: 80 },
});

// Bullet whose final run is a clickable hyperlink. Usage:
//   BULLET_LINK("Label - description (", "https://...", "EIA STEO May 2026", ")")
const BULLET_LINK = (prefix, href, linkText, suffix = "") => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [
    new TextRun(prefix),
    new ExternalHyperlink({
      link: href,
      children: [new TextRun({ text: linkText, style: "Hyperlink",
                               color: "0563C1", underline: {} })],
    }),
    new TextRun(suffix),
  ],
  spacing: { after: 80 },
});

// ── Tables ───────────────────────────────────────────────────────────
const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };

function buildTable(headers, rows, colWidths) {
  // colWidths in DXA, must sum to table width (9360 for US Letter @ 1" margins)
  const tableWidth = colWidths.reduce((a, b) => a + b, 0);
  const headerRow = new TableRow({
    children: headers.map((h, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      shading: { fill: "DDEBF7", type: ShadingType.CLEAR },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun({ text: h, bold: true })] })],
    })),
  });
  const dataRows = rows.map(r => new TableRow({
    children: r.map((c, i) => new TableCell({
      borders,
      width: { size: colWidths[i], type: WidthType.DXA },
      margins: { top: 80, bottom: 80, left: 120, right: 120 },
      children: [new Paragraph({ children: [new TextRun(String(c))] })],
    })),
  }));
  return new Table({
    width: { size: tableWidth, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

// ────────────────────────────────────────────────────────────────────
//  CONTENT
// ────────────────────────────────────────────────────────────────────
const content = [
  // ── PROJECT DESCRIPTION ───────────────────────────────────────────
  H1("Project description"),
  P("Optimization of a 6-month operating policy (1 June 2026 → 1 December 2026) for a pair of 100-MW data centers in the ERCOT region — Houston (HB_HOUSTON) and West Texas (HB_WEST) — covering allocation of compute capacity between training and inference, timing of new model releases, and procurement of grid power. The framework combines a deterministic linear program (LP) solving each hour's decisions for a given (training cadence, procurement) policy with a Monte-Carlo wrapper that simulates joint price paths and selects the policy maximizing expected profit under uncertainty."),

  // ── PROJECT SETUP ─────────────────────────────────────────────────
  H1("Project setup"),
  H2("3 main decisions"),
  BULLET("Training vs. inference compute split each hour at each site"),
  BULLET("Power procurement at each site: RT LMP vs. tolling (Houston only — no gas plant available at West) and BESS dispatch (charge from grid, discharge to data center, or sell back to grid)"),
  BULLET("Frequency of frontier-model retraining (cadence in days). Higher cadence keeps the deployed model closer to peak revenue but takes compute away from inference; lower cadence preserves inference capacity but lets revenue decay"),

  // ── ASSIGNED TASKS ────────────────────────────────────────────────
  H1("Assigned Tasks and Deliverables"),
  P("The prescribed task entails employing real-options analysis to design an economically viable operating policy for allocation and timing for incurring training cost as well as power procurement during the next 6 months (starting 1 June 2026 to 1 December 2026) with corresponding profitability (i.e., volatility-dependent conditional payoff) estimates during this period."),
  BULLET("Detailed description of the process of analysis, motivation/rationale justifying the methodology, and all assumptions."),
  BULLET("Value and estimate breakeven as well as marginal profitability increases for tolling fixed-lease-rate battery storage (BESS) at each location with recommendations as to under what market conditions either or both of these tolling arrangements would be economically viable."),
  BULLET("Substantive description of wind-solar intermittency in the context of MIHR citing the ERCOT data portal, and the contingency of the prescribed unscheduled outage scenarios."),

  // ── TRAINING + INFERENCE ──────────────────────────────────────────
  H1("Training + Inference"),

  H2("Training"),
  H3("Power and computational requirements"),
  P("Each model release k has a compute requirement that we project from its training-start date in three steps: training_start_date → projected parameter count → projected training FLOPS → required compute-MWh."),

  H3("Parameter projection"),
  P("Parameter counts in notable AI systems have grown exponentially. We fit a log-linear regression of log10(params) on Excel-serial date using the Epoch AI \"Parameters in notable artificial intelligence systems\" dataset with a post-2020 filter. The post-2020 cut produces a steeper, more recent trend that better matches frontier model sizes; the post-2010 alternative is documented in the code (`fit_growth_curves.py`) for comparison."),
  P("Post-2020 fit (n = 395 observations, R² ≈ 0.30):"),
  PR({ text: "log10(params) = −49.6585 + 1.32043 × 10⁻³ · day_serial", italics: true }),
  P("That gives a parameter-count doubling time of ~228 days. We then apply a 5× competitiveness multiplier (planning-doc convention) so projections track 2026 frontier-class models (DeepSeek 1.6T, GPT-class 1.7T, etc.) rather than the dataset-wide average — the regression line captures the average researcher, including small academic releases that drag the trend down, while we have to compete at frontier scale."),
  P("Projected post-multiplier parameter counts at planning-doc reference dates:"),
  buildTable(
    ["Release", "Training start", "Params (post-5×)", "Pre-multiplier"],
    [
      ["R1 (initial)", "2026-06-01", "1.02 × 10¹²", "2.04 × 10¹¹"],
      ["R2", "2026-06-22", "1.09 × 10¹²", "2.18 × 10¹¹"],
      ["R3", "2026-08-22", "1.31 × 10¹²", "2.62 × 10¹¹"],
      ["R4", "2026-10-22", "1.58 × 10¹²", "3.16 × 10¹¹"],
      ["R5", "2026-12-22", "1.90 × 10¹²", "3.80 × 10¹¹"],
    ],
    [1500, 1700, 3200, 2960],
  ),
  P("These figures are derived in `assumptions.project_params(training_start_date)`."),

  H3("FLOPS projection"),
  P("Training compute follows a power law in parameter count. We fit log10(petaFLOPS) vs. log10(params) on the Epoch AI \"Training computation vs. parameters\" dataset (n = 457, R² ≈ 0.84):"),
  PR({ text: "log10(petaFLOPS) = −9.8192 + 1.7187 · log10(params)", italics: true }),
  P("A 1.72 exponent matches Chinchilla-style scaling (FLOPS ∝ params × tokens, with tokens ∝ params). With the post-2020 parameter projection and the 5× multiplier, the projected training-FLOPS per release is:"),
  buildTable(
    ["Release", "Training start", "Training petaFLOPS", "FLOPS"],
    [
      ["R1", "2026-06-01", "6.64 × 10¹⁰", "6.64 × 10²⁵"],
      ["R2", "2026-06-22", "7.41 × 10¹⁰", "7.41 × 10²⁵"],
      ["R3", "2026-08-22", "1.02 × 10¹¹", "1.02 × 10²⁶"],
      ["R4", "2026-10-22", "1.40 × 10¹¹", "1.40 × 10²⁶"],
      ["R5", "2026-12-22", "1.93 × 10¹¹", "1.93 × 10²⁶"],
    ],
    [1500, 1700, 3000, 3160],
  ),
  P("Derived in `assumptions.project_petaflops(training_start_date)`."),

  H3("Hardware and FLOPS → MWh conversion"),
  P("Each data center holds 90,000 H-100-class GPUs at 80 MW of compute capacity (180,000 GPUs and 160 MW compute across both sites). H-100 SXM5 and H-100 PCIe have different sustained throughputs; SXM is generally better for training. We model an aggregate effective rate built from a configurable SXM/PCIe split:"),
  buildTable(
    ["Parameter", "Default value", "Notes"],
    [
      ["H100_SXM_SUSTAINED_TFLOPS_PER_SEC", "500 TF/s", "≈ 50 % of FP8-dense theoretical 989 TF/s. ⚠ TBD"],
      ["H100_PCIE_SUSTAINED_TFLOPS_PER_SEC", "380 TF/s", "≈ 50 % of FP8-dense theoretical 756 TF/s. ⚠ TBD"],
      ["SXM_FRACTION_DEFAULT", "0.60", "60 % SXM / 40 % PCIe. ⚠ TBD"],
      ["FLOPS_PER_COMPUTE_MWH", "1.83 × 10²¹", "Derived: GPUs × (split · TF/s) × 3600 / 80 MW"],
    ],
    [2700, 1400, 5260],
  ),
  P("Aggregate sustained throughput at 100 % compute utilization across both sites = 81.4 PFLOP/s = 2.93 × 10²³ FLOPS/hour. Dividing the per-release FLOPS by FLOPS_PER_COMPUTE_MWH gives the compute-MWh needed for that release. Multiplying by PUE = 1.25 converts to grid-MWh, which is what the LP's `train` and `inf` variables track."),

  H3("Three core decisions, recap"),
  BULLET("Training cadence (days between releases). Treated as a discrete sweep over candidate values, evaluated in expectation over MC price paths."),
  BULLET("SXM vs PCIe split. Currently collapsed into a single aggregate FLOPS_PER_COMPUTE_MWH because the underlying per-workload sustained rates are flagged TBD in the planning doc. Easy to split when finalized."),
  BULLET("Hourly training/inference split per site. The LP picks these endogenously given the cadence and price paths."),

  H3("First release: 100 % compute"),
  P("The initial release R1 begins 1 June 2026 and runs at 100 % compute utilization on both sites — no inference revenue accrues during R1's window. R1's window length is therefore set by compute-need / max-compute-rate:"),
  PR({ text: "R1_duration = project_compute_mwh(2026-06-01) / (2 × 80 MW · 24 h) ≈ 36,289 / 3,840 ≈ 9.5 → 10 days", italics: true }),
  P("All subsequent releases R(k+1) start at R(k)'s release date and run for the chosen cadence_days, with both training and inference allowed in those windows."),

  // ── INFERENCE ─────────────────────────────────────────────────────
  H2("Inference"),
  H3("Basic constraints"),
  BULLET("Inference can only use compute capacity not currently being used for training. Implemented as the LP's per-site compute cap: train + inf ≤ 100 grid-MWh/hr (= 80 compute-MWh/hr)."),
  BULLET("Token revenue at any hour must cover marginal power cost. The LP enforces this implicitly via its profit objective: an additional MWh of inference is only taken if its revenue exceeds its grid cost."),
  BULLET("Maximum request rate is such that power/computational cost does not exceed that unused by training, in any hour."),

  H3("Revenue per MWh"),
  P("Per the RFP, a 100 % allocation of 80 MW compute to inference produces 5 trillion tokens/day per site. This pins our conversion factor:"),
  PR({ text: "TOKENS_PER_COMPUTE_MWH = 5 × 10¹² / (80 × 24) ≈ 2.604 × 10⁹ tokens/cMWh", italics: true }),
  P("Token pricing follows GPT-5.4Pro on benchlm.ai with the RFP-specified 2/3 input + 1/3 output revenue mix:"),
  PR({ text: "blended rate = (2/3) × $30 + (1/3) × $180 = $80 per million tokens", italics: true }),
  P("That implies an inference revenue per compute-MWh of $208,333 (at peak, no decay); after PUE conversion, $166,667 per grid-MWh. This is the peak revenue an hour earns when the deployed model is at its newest. Per-hour revenue then declines via the token-decay path described below."),

  H3("Token-price decay between releases"),
  P("From the planning-doc observation that frontier token prices halve every couple of months, we model the per-hour inference revenue rate as:"),
  PR({ text: "rev_inf[h] = base_rev × multiplier_of_current_release × 0.5 ^ (days_since_release / 60)", italics: true }),
  P("Where `current_release` is the most-recent release as of hour h. Halflife defaults to 60 days; sensitivity to 30/45/60/90/120 days is provided in `halflife_sensitivity.py`."),

  H3("Per-release multipliers (token cost / quality)"),
  P("Each release carries a `token_revenue_multiplier`. Four schemes are available, configurable per-run:"),
  buildTable(
    ["Scheme", "Multiplier rule", "Captures"],
    [
      ["constant", "1.0 for every release", "No generation-over-generation differentiation; only the decay sawtooth matters"],
      ["quality_uplift", "uplift_factor^k for release k", "Each new release captures more value because it's a better model"],
      ["market_decay", "0.5^(release_t_days/60)", "Each new release earns less because the consumer market price has fallen"],
      ["doc_blended", "quality_uplift × market_decay", "Planning-doc story: quality rises but market deflates simultaneously"],
    ],
    [1500, 3000, 4860],
  ),
  P("Default for the headline run is `doc_blended` with `uplift_factor = 1.5`."),

  H3("Revenue at the hour level"),
  P("Total inference revenue per hour at a site, given the LP picked inf grid-MWh of inference:"),
  PR({ text: "revenue[h, s] = inf[h, s] × rev_inf[h]", italics: true }),
  P("Aggregated across hours and sites and netted against power costs (LMP/toll/BESS-charge) and BESS lease (if applicable), this is the LP's objective."),

  // ── CONVERSION ────────────────────────────────────────────────────
  H1("Conversion (compute → grid-MWh)"),
  P("The LP's training and inference decision variables are in grid-MWh — the same units as the power-procurement variables — because compute capacity converts to grid power at PUE = 1.25. Key relationships:"),
  buildTable(
    ["Quantity", "Formula", "Value (default)"],
    [
      ["Power Use Effectiveness", "Grid MWh / Compute MWh", "1.25"],
      ["Per-site grid power cap", "RFP", "100 MWh/hr"],
      ["Per-site compute capacity", "Grid cap ÷ PUE", "80 compute-MWh/hr"],
      ["Both-site grid cap", "200 MWh/hr", "= 4,800 MWh/day"],
      ["Both-site compute cap", "160 compute-MWh/hr", "= 3,840 cMWh/day"],
      ["FLOPS per compute-MWh", "Σ_GPU type frac · TF/s · 3600 / 80 MW", "1.83 × 10²¹"],
      ["Tokens per compute-MWh", "5T tokens/day ÷ (80 MW · 24 h)", "2.60 × 10⁹"],
    ],
    [2400, 3500, 3460],
  ),
  P("Constraints (planning doc):"),
  BULLET("Per-site grid draw g_lmp + g_toll ≤ 100 MWh/hr × capacity_factor"),
  BULLET("Aggregate grid draw across both sites ≤ 200 MWh/hr"),
  BULLET("Per-site train + inf ≤ 100 grid-MWh/hr (≡ 80 compute-MWh/hr after PUE)"),
  BULLET("Aggregate train + inf ≤ 200 grid-MWh/hr (≡ 160 compute-MWh)"),
  BULLET("Compute-clearing: g_lmp + g_toll + dis_dc = train + inf (LP balance equation)"),
  BULLET("RFP daily training floor: Σ train per day, summed across both sites, ≥ 500 MWh-grid"),

  // ── POWER ─────────────────────────────────────────────────────────
  H1("Power"),
  H2("Grid LMP (HB_HOUSTON, HB_WEST)"),
  P("Hourly Day-Ahead Market settlement-point prices for the two ERCOT hubs are sourced from the ERCOT ISO publishing site (xlsx in `data/`). For the 6-month horizon, we use the actual 2025 June-November DAM hourly prices, shifted forward one calendar year, as a deterministic proxy. For the headline real-options analysis these prices are replaced by N Monte-Carlo paths simulated from a seasonal Ornstein-Uhlenbeck model calibrated on the full 2025 actuals."),
  P("Note: the RFP requests RT-LMP. DAM is the closest available proxy in the repo; RT is typically more volatile and would slightly increase the value of tolling and BESS arbitrage."),

  H2("Henry Hub gas (for tolling)"),
  P("Daily Henry Hub spot prices from the EIA are used in the Houston tolling cost formula. Loaded from `HH_full.csv`."),

  H2("Tolling at Houston (period-long option, hourly exercise)"),
  P("Tolling is structured as a binary period-long contract decision (`Scenario.use_houston_tolling`). When the contract is signed, the LP gets an hourly option to draw up to TOLL_MAX_MW of power at the tolling cost — exercised only when LMP > toll cost. Toll variable cost per MWh:"),
  PR({ text: "toll_cost[$/MWh] = (HH_gas[$/MMBtu] + $3/MMBtu O&M) × 9.5 MMBtu/MWh ≈ $57/MWh at $3 gas", italics: true }),
  P("Heat rate is 9,500 BTU/kWh per the RFP — typical of an efficient simple-cycle peaker. West Texas has no tolling option (no gas plant available)."),
  P("Tolling parameters (currently default-modelled with no fixed surcharge):"),
  buildTable(
    ["Parameter", "Default", "Notes"],
    [
      ["TOLL_HEAT_RATE_BTU_PER_KWH", "9,500", "RFP — simple-cycle peaker"],
      ["TOLL_VOM_PER_MMBTU", "$3/MMBtu", "RFP — variable O&M premium"],
      ["TOLL_MAX_MW", "100 MWh/hr", "Hourly cap = site grid cap (assumption)"],
      ["Scenario.toll_max_mwh_per_day", "None (unconstrained)", "Daily MWh cap on Houston toll. Empirical brackets in assumptions.py: TOLL_DAILY_CAP_PEAKER=720, _INTERMEDIATE=1500, _NEAR_NAMEPLATE=2280 (anchored to EIA SCGT capacity-factor history). --toll-cap-sweep runs all four on the sweep driver."],
      ["TOLL_FIXED_SURCHARGE_PER_MWH", "$0", "⚠ TBD capacity payment (RFP didn't specify)"],
    ],
    [3000, 1500, 4860],
  ),

  H2("BESS (40 MW / 160 MWh / 92 % RTE at each site)"),
  P("Battery storage is modeled as a tolling agreement (physical or virtual) for 6 months. The contract is binary per site (`Scenario.bess_sites` can be any subset of {HOUSTON, WEST}). When active at a site, the LP gets four hourly decisions:"),
  BULLET("ch[h, s]: MWh charged from the grid (drawn at LMP)"),
  BULLET("dis_dc[h, s]: MWh discharged to the data center (substitutes for grid draw at LMP)"),
  BULLET("dis_grid[h, s]: MWh discharged and sold back to the grid at LMP"),
  BULLET("soc[h, s]: state of charge at hour h, bounded 0 ≤ soc ≤ 160 MWh"),
  P("BESS dynamics:"),
  PR({ text: "soc[h+1] = soc[h] + √0.92 × ch[h] − (dis_dc[h] + dis_grid[h]) / √0.92", italics: true }),
  P("Charge and combined discharge each capped at 40 MWh/hr; round-trip efficiency 92 % (= per-direction √0.92 ≈ 0.959). The 6-month lease per site is amortized from the RFP-stated cost structure:"),
  PR({ text: "lease/site = $60M capex / 15 yr / 2 + $2M opex/yr / 2 = $3M for 6 months", italics: true }),
  P("Or $6M total if BESS is active at both sites. This fixed cost is excluded from the LP objective directly (it's a constant) but subtracted in `cost_breakdown` so the per-scenario profit numbers reflect it."),

  // ── MODEL DYNAMIC ─────────────────────────────────────────────────
  H1("Model Dynamic"),
  H2("Decision variables"),
  P("Per hour h ∈ {0..4391} and per site s ∈ {HOUSTON, WEST}:"),
  buildTable(
    ["Variable", "Units", "Bounds", "Meaning"],
    [
      ["g_lmp[h, s]", "grid-MWh", "0 .. 100", "Power drawn at RT LMP"],
      ["g_toll[h, s]", "grid-MWh", "0 .. 100, 0 at WEST", "Power drawn under Houston tolling"],
      ["train[h, s]", "grid-MWh", "≥ 0", "Compute allocated to training"],
      ["inf[h, s]", "grid-MWh", "≥ 0", "Compute allocated to inference"],
      ["ch[h, s]", "MWh", "0 .. 40 (BESS sites)", "BESS charge from grid"],
      ["dis_dc[h, s]", "MWh", "≥ 0", "BESS discharge to data center"],
      ["dis_grid[h, s]", "MWh", "≥ 0", "BESS discharge sold at LMP"],
      ["soc[h, s]", "MWh", "0 .. 160", "BESS state of charge"],
    ],
    [1900, 1500, 1900, 4060],
  ),

  H2("Model-variable parameters"),
  BULLET("Training cadence (days between releases). Default candidate set: [10, 15, 20, 25, 30, 45, 60, 75, 90, 120, 150, 180]. Filter retains those whose smallest non-initial release's natural training rate is ≥ 500 MWh-grid/day AND whose largest release's required rate is ≤ 4,800 MWh-grid/day. Typical filtered set: [25, 30, 45, 60, 75, 90]."),
  BULLET("Token-multiplier scheme (per-release revenue scaling). Default `doc_blended`."),
  BULLET("Procurement scenario (use_houston_tolling, bess_sites). Default everything-on; Phase C optimizes."),
  BULLET("Number of Monte-Carlo paths. Default 50 for production runs."),

  H2("Objective"),
  P("Maximize expected profit across MC price paths:"),
  PR({ text: "max  Σ_h Σ_s ( rev_inf[h] · inf[h, s]  +  LMP[h, s] · dis_grid[h, s] )", italics: true }),
  PR({ text: "    − Σ_h Σ_s ( LMP[h, s] · g_lmp[h, s]  +  toll_cost[h] · g_toll[h, s]  +  LMP[h, s] · ch[h, s] )", italics: true }),
  PR({ text: "    − BESS_6mo_lease × |bess_sites|", italics: true }),

  H2("Constraints"),
  BULLET("Per-site grid draw cap: g_lmp + g_toll ≤ 100 MWh/hr × capacity_factor"),
  BULLET("Per-site compute cap: train + inf ≤ 100 MWh-grid/hr (= 80 compute-MWh/hr)"),
  BULLET("Power balance: g_lmp + g_toll + dis_dc = train + inf (LP balance; ensures power into the DC matches compute load)"),
  BULLET("Tolling at Houston only: g_toll[h, WEST] = 0"),
  BULLET("Houston toll capacity: g_toll[h, HOUSTON] ≤ TOLL_MAX_MW (× capacity_factor)"),
  BULLET("Optional daily toll MWh cap: Σ_h g_toll[h, HOUSTON] per day ≤ Scenario.toll_max_mwh_per_day (peaker 720 / intermediate 1500 / near-nameplate 2280 — EIA-anchored brackets)"),
  BULLET("BESS power: ch ≤ 40 MWh/hr, dis_dc + dis_grid ≤ 40 MWh/hr"),
  BULLET("BESS SOC: 0 ≤ soc ≤ 160 MWh, soc[h+1] = soc[h] + √0.92 × ch − (dis_dc + dis_grid) / √0.92"),
  BULLET("BESS starts and ends at SOC = 0 (no inventory at horizon endpoints)"),
  BULLET("Per-release training: Σ_h Σ_s train[h, s] over R_k's window ≥ project_compute_mwh(R_k.start) × PUE"),
  BULLET("R1 initial: inf[h, s] = 0 for all h in R1's window (100 % compute → training)"),
  BULLET("Outside any release window: train[h, s] = 0 (unless schedule is empty, in which case the daily floor governs)"),
  BULLET("RFP daily training floor (mandatory): Σ_s,h-in-day train[h, s] ≥ 500 MWh-grid/day"),

  H2("Optimization workflow (run_planning_doc.py)"),
  P("Profit is maximized in four sequential phases:"),
  H3("Phase A — Cadence selection (procurement = all on)"),
  P("For each candidate cadence c (after filter), solve the LP across N MC price paths in parallel via a ProcessPool. Mean per-path profit is the score for c. Stage 1 sweeps the filtered broad set; Stage 2 refines six cadences ±30 % around the Stage-1 winner. Winner is the cadence with highest mean profit."),
  H3("Phase B — Locked-cadence diagnostic (procurement = all on)"),
  P("At the Phase-A winning cadence, re-solve the LP on every path and report averaged-across-paths metrics: cost breakdown, profit distribution, procurement mix. This is a marginal-cost view — the LP \"uses\" BESS even when the lease is net-negative because the lease is a sunk constant from the LP's perspective."),
  H3("Phase C — Procurement optimization (full-cost view, lease included)"),
  P("At the locked cadence, sweep eight procurement combinations: toll ∈ {off, on} × BESS-sites ∈ {none, Houston, West, both}. For each combo, solve N paths and average profit including the BESS lease as a fixed-cost subtraction. Pick the combo with highest mean profit; this is the optimal procurement under full-cost accounting."),
  H3("Verification — Cadence under optimal procurement"),
  P("Re-solve a tight ±30 % cadence neighborhood under Phase C's optimal procurement. Confirms the cadence winner doesn't shift when negative-NPV options are stripped out (in practice never does, because cadence-vs-cadence profit gaps are ~$3 B while procurement-vs-procurement gaps are ~$5 M)."),
  H3("Final output"),
  P("Re-solve the LP on every MC path with the (verified cadence, optimal procurement) policy and save:"),
  BULLET("Per-path hourly schedule in long format (all decision variables: g_lmp, g_toll, train, inf, compute-MWh, FLOPS, tokens, BESS dispatch if enabled)."),
  BULLET("Averaged-across-paths hourly schedule with ±std for every variable."),
  BULLET("Per-cadence mean/std/percentile summary CSV."),
  BULLET("Console: first 24 hours at HOUSTON with mean ± std annotations."),

  H2("Inputs at a glance"),
  buildTable(
    ["Group", "Item", "Source / Default"],
    [
      ["Power", "Hourly RT LMP (HB_HOUSTON, HB_WEST)", "ERCOT DAM 2025, shifted +1 yr; MC paths from OU calibration"],
      ["Power", "Tolling cost", "(HH_daily + $3/MMBtu) × 9.5 MMBtu/MWh"],
      ["Power", "BESS 6-month lease per site", "$3 M (= $60 M / 15 yr / 2 + $2 M / 2)"],
      ["Power", "Facility cap", "200 MWh/hr (= 100/site)"],
      ["Compute", "Compute cap", "160 cMWh/hr (= 80/site after PUE 1.25)"],
      ["Compute", "Hardware throughput", "FLOPS_PER_COMPUTE_MWH = 1.83 × 10²¹"],
      ["Compute", "Min daily training", "500 MWh-grid/day, system-total (mandatory)"],
      ["Training", "Param projection", "log10(P) = −49.66 + 1.32e-3·day (post-2020 fit, 5× multiplier)"],
      ["Training", "FLOPS projection", "log10(petaFLOPS) = −9.82 + 1.72·log10(P)"],
      ["Training", "R1 fixed", "Starts 6/1/2026, 100 % compute, ~10 days"],
      ["Revenue", "Token price (peak)", "$30/MM input + $180/MM output ⇒ $80/MM blended"],
      ["Revenue", "Tokens per compute-MWh", "2.604 × 10⁹"],
      ["Revenue", "Decay halflife", "60 days (sensitivity available)"],
    ],
    [1300, 3000, 5060],
  ),

  // ── OUTSTANDING WORK ──────────────────────────────────────────────
  H1("Outstanding Work: Parameters and Assumptions to Finalize"),
  P("Items below are open questions whose resolution will sharpen the model. Each is wired into the code with a sensible default so the current results are usable, but the defaults should be revisited once authoritative numbers are available."),

  H2("Hardware throughput (FLOPS → MWh conversion)"),
  BULLET_R(
    { text: "H-100 SXM sustained throughput", bold: true },
    " — currently 500 TF/s (≈ 50 % of FP8-dense theoretical 989 TF/s). Need an authoritative sustained-FP8 number for our intended training workload (mix of attention, MLP, comms overhead).",
  ),
  BULLET_R(
    { text: "H-100 PCIe sustained throughput", bold: true },
    " — currently 380 TF/s (≈ 50 % of FP8-dense 756 TF/s). Same caveat as SXM.",
  ),
  BULLET_R(
    { text: "SXM vs PCIe split", bold: true },
    " — currently 60 / 40. Drives the aggregate FLOPS_PER_COMPUTE_MWH; today it is collapsed into a single number. Once the split is set, we can also split the LP's `train` variable per hardware class (SXM preferred for training, PCIe biased to inference).",
  ),
  H2("Inference revenue model"),
  BULLET_R(
    { text: "Token-price projection", bold: true },
    " — currently $30/MM input + $180/MM output blended via the RFP-stated 2/3 + 1/3 mix to $80/MM. This is the spot benchlm.ai rate for GPT-5.4Pro; need a forward-looking curve, not a single number, to better match the 6-month horizon.",
  ),
  BULLET_R(
    { text: "Token-price decay halflife", bold: true },
    " — currently 60 days, with sensitivity at 30/45/60/90/120 days in `halflife_sensitivity.py`. The 60-day default is supported by 2024–2025 frontier-tier price observations but is a strong driver of optimal cadence; a defensible point-estimate (or distribution) is needed.",
  ),
  BULLET_R(
    { text: "Tokens per request", bold: true },
    " — not currently in the model. The RFP requests it; we use a per-MWh tokens conversion instead. Adding it would let us express revenue at the request level (price × requests/hr) rather than the MWh level.",
  ),
  BULLET_R(
    { text: "Per-release quality multiplier", bold: true },
    " — currently `doc_blended` with uplift_factor = 1.5 (i.e., each release is 1.5× more valuable per token than the previous one before market decay). Plausible but not measured.",
  ),

  H2("Tolling contract"),
  BULLET_R(
    { text: "Scenario.toll_max_mwh_per_day", bold: true },
    " — daily MWh cap on Houston tolling. Three empirically-anchored brackets exposed in assumptions.py: peaker (720 MWh/day, 30 % of nameplate × 24 h — matches EIA's 9.6–14.1 % SCGT capacity-factor range), intermediate (1,500 MWh/day, ~63 % — IPP load-following toll convention, recommended headline default), and near-nameplate (2,280 MWh/day, ~95 % — availability-only haircut). --toll-cap-sweep on power_procurement_sweep.py reports marginal toll value as a function of the cap.",
  ),
  BULLET_R(
    { text: "Fixed surcharge / capacity payment", bold: true },
    " — currently $0/MWh on the variable side and no annual fixed payment. Real tolling contracts typically include both. A non-zero fixed surcharge would change Phase C's decision about whether to sign the contract at all.",
  ),
  BULLET_R(
    { text: "Heat rate", bold: true },
    " — currently 9,500 BTU/kWh per the RFP. This is consistent with an efficient simple-cycle peaker; assumed firm.",
  ),

  H2("BESS contract"),
  BULLET_R(
    { text: "Lease structure", bold: true },
    " — currently $60 M capex amortized over 15 yr + $2 M opex/yr, half-year prorate ⇒ $3 M / site / 6 months. Need confirmation that this is the actual tolling-style lease structure for the prescribed BESS rather than an outright-buy amortization.",
  ),
  BULLET_R(
    { text: "Round-trip efficiency", bold: true },
    " — currently 92 % (√ on each leg ≈ 0.959). RFP-stated; assumed firm.",
  ),
  BULLET_R(
    { text: "Degradation", bold: true },
    " — not currently modelled (6-month horizon is short enough that this is plausibly second-order, but should be noted).",
  ),

  H2("Power-price input"),
  BULLET_R(
    { text: "DAM vs RT LMP", bold: true },
    " — RFP requests RT-LMP; we use DAM as the closest available proxy (the project repo's CSVs are DAM). RT is typically more volatile, which would slightly increase the value of both tolling (option-like) and BESS arbitrage.",
  ),
  BULLET_R(
    { text: "Forward-curve drift", bold: true },
    " — MC paths are simulated from OU calibrated on 2025 actuals. Drift is now a CLI knob (--gas-drift-pct, --power-drift-pct on run_monte_carlo.py / run_planning_doc.py / power_procurement_sweep.py) that adds a log-space shift to each series' long-run mean via monte_carlo.apply_drift(). Baseline 2026 = 0 % both, consistent with EIA May-2026 STEO (HH 2026 forecast $3.50/MMBtu vs 2025 actual $3.53). Geopolitical oil overlay: a +30 % Brent shock translates to gas_drift_pct ≈ 0.06 (Brent→HH elasticity ≈ 0.2 via LNG-pull) and power_drift_pct ≈ 0.03 (HH→LMP elasticity ≈ 0.5 via gas-on-margin pass-through).",
  ),
  BULLET_R(
    { text: "Number of MC paths", bold: true },
    " — currently default 50 for production runs. 200+ would tighten confidence intervals on procurement decisions where the gap is small (Phase-C gaps are ~$5 M while paths-stdev is ~$30 M).",
  ),

  H2("Constraints from the RFP — partially covered"),
  P("The FTG repo (ltemry/FTG-Final-Project) contains `src/phase4_intermittency_stress.py`, which addresses intermittency and tail-risk events indirectly — by reading them out of LMP signatures rather than modelling wind/solar generation directly. We have vendored the OU calibration, MC simulator, AND (as of this revision) the stress-overlay logic from that repo. What's covered vs what's still open:"),
  BULLET_R(
    { text: "Unscheduled-outage / Uri-style stress (ported, optional toggle)", bold: true },
    " — `model/stress.py` exposes four scenarios from FTG phase 4: none (default), mild (72 h, $200–400/MWh, p = 0.50), moderate (96 h, $500–1500/MWh + $20/MMBtu gas, p = 0.20), uri_full (100 h, $5000–9000/MWh + $250/MMBtu gas, p = 0.05). When `run_planning_doc.py --stress <name>` is set, the chosen overlay is applied to a fraction of the MC paths AFTER the OU simulation and BEFORE the LP solve, on both ERCOT hubs simultaneously (system-wide scarcity event). Default is `none`, so headline results are unchanged. Use it as a sensitivity / stress test — expectation is that the toll option's value rises materially under moderate/uri_full.",
  ),
  BULLET_R(
    { text: "Wind-solar intermittency / MIHR (qualitative — still to report)", bold: true },
    " — phase 4 in the FTG repo computes diurnal LMP percentile profiles, the evening-ramp premium (hour-18 − hour-14, capturing solar dropoff), and negative-LMP frequency at HB_WEST (wind-oversupply proxy). These are LMP-implied signatures of renewable variability, which is consistent with the RFP's request for a substantive discussion citing ERCOT data. Action item: include these diagnostics in the report; the analysis logic exists, it just isn't a separate module in our codebase yet.",
  ),
  BULLET_R(
    { text: "Capacity-factor derate (true MIHR-style — still open)", bold: true },
    " — distinct from the LMP-signature view above. Our LP currently assumes capacity_factor = 1.0 (full 100 MW/site at every hour). A direct MIHR model would multiply the per-site grid cap by a stochastic capacity_factor[h] ≤ 1 driven by renewables + transmission. Not implemented; phase 4 doesn't do this either (it works on prices, not capacity).",
  ),

  // ── DATA SOURCES & CITATIONS ─────────────────────────────────────
  H1("Data sources and citations"),
  P("Vendored data files (used directly by the calibration / LP):"),
  BULLET("data/HH_full.csv - Henry Hub daily spot price ($/MMBtu), EIA Natural Gas Weekly. Source: eia.gov/dnav/ng/hist/rngwhhdD.htm."),
  BULLET("data/rpt.00013060.0000000000000000.DAMLZHBSPP_2025.xlsx - ERCOT 2025 Day-Ahead Market hourly settlement-point prices, HB_HOUSTON and HB_WEST. Source: ercot.com (Market Information / DAM SPP report)."),
  BULLET("data/artificial-intelligence-parameter-count.csv - Epoch AI parameter-count time series. Source: epochai.org (Notable AI Models dataset)."),
  BULLET("data/ai-training-computation-vs-parameters-by-researcher-affiliation.csv - Epoch AI training-compute vs parameters panel. Source: epochai.org."),

  P("External references used to anchor TBD/sensitivity inputs in this report:"),

  H2("Tolling daily MWh cap (TOLL_DAILY_CAP_PEAKER / INTERMEDIATE / NEAR_NAMEPLATE)"),
  BULLET_LINK("EIA Today in Energy (June 2023) - U.S. simple-cycle natural gas turbines operated at record highs in summer 2022. Anchors the peaker bracket: SCGT fleet annual capacity factor 9.6-14.1% (2017-2023), ~17% summer / ~10% off-season, ERCOT among regions above the national average. ",
    "https://www.eia.gov/todayinenergy/detail.php?id=55680",
    "eia.gov/todayinenergy/detail.php?id=55680"),
  BULLET_LINK("EIA Form 923 (plant-level operations data) - net generation and heat input by prime-mover, used to verify the SCGT capacity-factor range above and to derive an MDQ-equivalent envelope. ",
    "https://www.eia.gov/electricity/data/eia923/",
    "eia.gov/electricity/data/eia923"),
  BULLET_LINK("Modo Energy - ERCOT BESS tolling agreement explainer. Establishes that current ERCOT tolling contracts give the offtaker direct dispatch rights over the full asset envelope (near-nameplate convention). ",
    "https://modoenergy.com/research/en/battery-bess-offtake-tolling-agreements-route-market-contracts-ercot-explainer-part-one",
    "modoenergy.com/.../ercot-explainer-part-one"),
  BULLET_LINK("GridStor - Fortune 500 tolling pact for a 150 MW / 350 MWh ERCOT battery (Dec 2025). Recent comparable disclosing contract structure for the near-nameplate bracket. ",
    "https://www.stocktitan.net/news/GS/grid-stor-announces-tolling-agreement-and-start-of-construction-for-86v9on13jxdv.html",
    "stocktitan.net/.../gridstor-tolling-agreement"),
  BULLET_LINK("Entergy MUCPA - Capacity Sale and Tolling Agreement RFP (template). Reference document showing standard daily-MDQ contract structure for natural-gas-fired tolling. ",
    "https://rfp.entergy.com/entrfp/send/Final%20RFP%20MUCPA%20-%20Tolling.pdf",
    "rfp.entergy.com/.../MUCPA-Tolling.pdf"),

  H2("Forward-curve drift (--gas-drift-pct / --power-drift-pct)"),
  BULLET_LINK("EIA Short-Term Energy Outlook (May 2026) - natural gas section. Baseline: 2025 actual HH = $3.53/MMBtu, 2026 forecast = $3.50/MMBtu (essentially flat - hence default gas_drift_pct = 0). 2026 LNG export forecast = 17.0 Bcf/d (up from 15.1 in 2025), near peak export-complex capacity. ",
    "https://www.eia.gov/outlooks/steo/report/natgas.php",
    "eia.gov/outlooks/steo/report/natgas.php"),
  BULLET_LINK("EIA STEO May 2026 (full PDF) - the primary source for the Brent forecast that drives the geopolitical-shock overlay. Reports Brent $106/b May-Jun 2026 and $115/b 2Q peak amid Strait of Hormuz disruption; ~10.5 Mbbl/d of Mideast production shut-in. ",
    "https://www.eia.gov/outlooks/steo/pdf/steo_full.pdf",
    "eia.gov/outlooks/steo/pdf/steo_full.pdf"),
  BULLET_LINK("EIA Today in Energy - Henry Hub spot prices to fall slightly in 2026, rise in 2027. Confirms the EIA's view that higher 2026 Brent supports associated-gas production (bearish HH), partially offsetting the LNG-pull (bullish HH) channel. ",
    "https://www.eia.gov/todayinenergy/detail.php?id=67004",
    "eia.gov/todayinenergy/detail.php?id=67004"),
  BULLET_LINK("EIA Press Release (May 12, 2026) - STEO revision amid continued Mideast disruption. Quantifies the Hormuz-closure assumption (closed until late May, shipping resumes June) used to size the +30% Brent shock scenario. ",
    "https://www.eia.gov/pressroom/releases/press588.php",
    "eia.gov/pressroom/releases/press588.php"),
  BULLET_LINK("Rigzone (May 20, 2026) - EIA lowers Henry Hub forecast for 2026, 2027. Documents the May-vs-April STEO revision ($3.67 -> $3.50/MMBtu) - useful for justifying baseline gas_drift_pct = 0 against a contemporaneous-news critique. ",
    "https://www.rigzone.com/news/usa_eia_lowers_henry_hub_price_forecast_for_2026_2027-20-may-2026-183738-article/",
    "rigzone.com/.../usa-eia-lowers-henry-hub-price-forecast"),
  BULLET_LINK("S&P Global - Texas summer 2025 power prices may top 2024 on weather and strong gas. Anchors the HH -> ERCOT LMP elasticity: Houston Ship Channel summer forwards ~$4/MMBtu (vs ~$2 in 2024) coincided with ERCOT Houston on-peak forwards $110-167/MWh (vs DAM $30-40/MWh in 2024). ",
    "https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/042325-outlook-2025-texas-summer-power-prices-may-top-2024-levels-on-weather-strong-gas",
    "spglobal.com/.../texas-summer-power-prices-2025"),
  BULLET_LINK("Potomac Economics - 2024 State of the Market Report for ERCOT. Source for implied heat-rate ranges (Figure 7) used to derive the HH->LMP pass-through elasticity (~0.5 in gas-on-margin hours). ",
    "https://www.potomaceconomics.com/wp-content/uploads/2025/06/2024-State-of-the-Market-Report.pdf",
    "potomaceconomics.com/.../2024-State-of-the-Market-Report.pdf"),

  // ── REPORT skeleton (left blank; user will fill in) ──────────────
  H1("Report"),
  P("(Sections below to be written; planning sections above describe the model setup and serve as input.)"),
  H2("Executive Summary"),
  H2("Model Setup"),
  H3("Inference + Training"),
  P("Data Inputs"),
  P("Assumptions"),
  P("Constraints"),
  H3("Power"),
  P("Data Inputs"),
  P("Assumptions"),
  P("Constraints"),
  H3("Workflow (Descriptive Model) & The Code"),
  H2("Results / Sensitivities"),
  H2("Analysis"),
  H2("Conclusion"),
];

// ────────────────────────────────────────────────────────────────────
//  DOCUMENT
// ────────────────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } }, // 11pt
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F4E79" },
        paragraph: { spacing: { before: 300, after: 200 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 140 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "3F3F3F" },
        paragraph: { spacing: { before: 160, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children: content,
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const out = path.join(ROOT, "Final Project Current Status Report.docx");
  fs.writeFileSync(out, buffer);
  console.log("Wrote", out, `(${buffer.length} bytes)`);
});
