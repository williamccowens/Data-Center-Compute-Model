"""
All numeric inputs for the data-center profit optimization.

Sources:
  RFP     = "FinalVersion_Financing the Grid_Project_2026-1.pdf"
  Plan    = "Final Project Planning.docx"
  benchlm = https://benchlm.ai/llm-pricing  (queried for GPT-5.4Pro)

Every figure that is NOT a direct quote from the RFP is flagged ASSUMPTION
so it can be overridden on the command line via run_optimization.py.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Tuple, Optional


# ── Time horizon ───────────────────────────────────────────────────────────
HORIZON_START = date(2026, 6, 1)
HORIZON_END   = date(2026, 12, 1)        # exclusive
# Note: RFP says "next 6 months (i.e., June-November)" — so we run 6/1 → 11/30.


# ── Sites ─────────────────────────────────────────────────────────────────
SITES = ("HOUSTON", "WEST")
HOUSTON = "HOUSTON"
WEST    = "WEST"

# Per-site nameplate (RFP)
SITE_POWER_CAPACITY_MW   = 100.0   # grid draw cap, both sites
SITE_COMPUTE_CAPACITY_MW = 80.0    # compute cap, both sites
PUE                      = 1.25    # grid MW per compute MW

# ─────────────────────────────────────────────────────────────────────────
# H-100 hardware spec — TBD pending project team's final numbers.
# Planning doc Decision 2: "SXM vs PCIe split + sustained TF/s for
# training and inference workloads is waiting on Srishti/Lili's estimate".
# Defaults below are PLACEHOLDERS calibrated to ~50% of theoretical FP8
# dense throughput (NVIDIA datasheet: SXM5 = 989 TF/s, PCIe = 756 TF/s) —
# typical of real, end-to-end training loops including comms/checkpoint
# overhead. SWAP THESE when the project team finalizes its numbers.
# Currently we collapse "training throughput" and "inference throughput"
# into the same number per GPU; the planning doc flagged these as
# potentially different. To split, add separate constants and route to
# FLOPS_PER_COMPUTE_MWH for training, INFERENCE_REV_PER_GRID_MWH for inference.
# ─────────────────────────────────────────────────────────────────────────
GPUS_PER_SITE = 90_000                        # RFP — fixed
H100_SXM_SUSTAINED_TFLOPS_PER_SEC  = 500.0    # ⚠️ TBD placeholder (~50% of FP8 dense)
H100_PCIE_SUSTAINED_TFLOPS_PER_SEC = 380.0    # ⚠️ TBD placeholder (~50% of FP8 dense)
SXM_FRACTION_DEFAULT = 0.60                   # ⚠️ TBD placeholder (60/40 default)

# Houston is the only site with tolling access (RFP)
TOLL_SITES = (HOUSTON,)


# ── Compute → tokens conversion (RFP) ─────────────────────────────────────
# "100% allocation of 80 MW capacity to inference → 5 trillion tokens/day"
TOKENS_PER_DAY_AT_FULL_INFERENCE = 5e12          # tokens / day, per site at 80 MW
TOKENS_PER_COMPUTE_MWH = TOKENS_PER_DAY_AT_FULL_INFERENCE / (80.0 * 24.0)
# = 2.604e9 tokens per compute-MWh


# ─────────────────────────────────────────────────────────────────────────
# Token pricing — partly TBD pending project team's final revenue model.
# Per-MM prices below come from benchlm.ai/llm-pricing for GPT-5.4Pro
# (RFP-specified) as the FRONTIER PEAK. Mix is RFP-fixed (2/3 input,
# 1/3 output). What's still TBD:
#   1. Per-release token-price projection (currently configurable via
#      `token_revenue_multiplier` on each TrainingRun — schemes: constant,
#      quality_uplift, market_decay, doc_blended).
#   2. Tokens-per-request and request-rate models. These are currently
#      ABSTRACTED into the RFP's 5T-tokens/day @ 80 MW relationship, which
#      is what fixes TOKENS_PER_COMPUTE_MWH. Once concrete numbers arrive,
#      replace TOKENS_PER_COMPUTE_MWH directly or split into separate
#      tokens/request × requests/MWh constants.
# ─────────────────────────────────────────────────────────────────────────
TOKEN_PRICE_INPUT_PER_MM  = 30.0    # benchlm.ai GPT-5.4Pro frontier peak
TOKEN_PRICE_OUTPUT_PER_MM = 180.0   # benchlm.ai GPT-5.4Pro frontier peak
INPUT_REVENUE_FRACTION    = 2.0 / 3.0   # RFP-fixed
OUTPUT_REVENUE_FRACTION   = 1.0 / 3.0   # RFP-fixed

# Blended $ per million tokens
TOKEN_REVENUE_PER_MM = (
    INPUT_REVENUE_FRACTION  * TOKEN_PRICE_INPUT_PER_MM
    + OUTPUT_REVENUE_FRACTION * TOKEN_PRICE_OUTPUT_PER_MM
)
# = $80 per MM tokens

# Revenue per compute-MWh of inference
INFERENCE_REV_PER_COMPUTE_MWH = TOKENS_PER_COMPUTE_MWH * TOKEN_REVENUE_PER_MM / 1e6
# = $208,333 per compute-MWh

# Revenue per grid-MWh of inference (since 1 grid MWh → 0.8 compute MWh under PUE)
INFERENCE_REV_PER_GRID_MWH = INFERENCE_REV_PER_COMPUTE_MWH / PUE
# = $166,666 per grid-MWh


# ── Training requirement (RFP) ────────────────────────────────────────────
# "daily average of at least 500 MW-hours committed to training tasks as a
#  cost incurred — at any time, at either location"
TRAINING_MIN_MWH_PER_DAY = 500.0   # grid MWh, summed across both sites


# ── Tolling at Houston (RFP) ──────────────────────────────────────────────
TOLL_HEAT_RATE_BTU_PER_KWH = 9500.0           # simple-cycle peaker, RFP
TOLL_HEAT_RATE_MMBTU_PER_MWH = TOLL_HEAT_RATE_BTU_PER_KWH * 1000.0 / 1e6  # 9.5
TOLL_VOM_PER_MMBTU         = 3.0              # RFP: $3/MMBTU premium above HH
TOLL_MAX_MW                = 100.0            # ASSUMPTION: toll covers full 100 MW site capacity
TOLL_FIXED_SURCHARGE_PER_MWH = 0.0            # ASSUMPTION: fixed toll fee not specified in RFP
# ── Tolling daily cap (RFP-flagged, value TBD) ────────────────────────────
# The RFP describes tolling as "a pre-specified maximum MW-hours of power
# available throughout each corresponding generation day" — i.e. a DAILY
# MWh cap on toll. The cap value is not given numerically in the RFP and
# is currently TBD. Set to None = no daily cap (only the hourly TOLL_MAX_MW
# applies). Set to a number (e.g. 1500.0 or 2400.0) to enforce.
TOLL_MAX_MWH_PER_DAY: float | None = None     # ⚠️ TBD pending RFP / contract spec

def tolling_cost_per_mwh(henry_hub_price: float) -> float:
    """Convert a daily Henry Hub price ($/MMBtu) → all-in toll cost in $/MWh."""
    return TOLL_HEAT_RATE_MMBTU_PER_MWH * (henry_hub_price + TOLL_VOM_PER_MMBTU) \
         + TOLL_FIXED_SURCHARGE_PER_MWH


# ── BESS (RFP) ────────────────────────────────────────────────────────────
BESS_POWER_MW          = 40.0      # discharge/charge cap per site
BESS_ENERGY_MWH        = 160.0     # nameplate stored energy
BESS_ROUND_TRIP_EFF    = 0.92
BESS_CAPEX             = 60e6      # $ per site
BESS_OPEX_PER_YEAR     = 2e6       # $ per site per year
BESS_LIFETIME_YEARS    = 15.0
# 6-month lease ≈ amortized capex + half the annual OPEX
BESS_6MO_LEASE_COST = (
    BESS_CAPEX / BESS_LIFETIME_YEARS / 2.0   # capex amortized 6 months
    + BESS_OPEX_PER_YEAR / 2.0               # opex 6 months
)
# = $3.0M per site for the 6-month horizon


# ── Planning-doc training framework ──────────────────────────────────────
# Source: "Final Project Planning .docx", section "Training + Inference".
#
# The planning doc identifies a sequence of model releases over the horizon,
# each requiring a fixed amount of compute (in petaFLOPS) determined by the
# model's parameter count. Below are the doc's stated requirements *with*
# the 5× parameter multiplier the team applied to match frontier models
# like DeepSeek/GPT-4/etc.
#
# Release-to-FLOPS map (from planning doc):
#     R1 (initial, 3-wk):  6/1  →  6/22   parameters 1.293T → 1.310e26 FLOPS
#     R2 (bimonthly):     6/22  →  8/22   parameters 1.351T → 1.413e26 FLOPS
#     R3 (bimonthly):     8/22  → 10/22   parameters 1.536T → 1.761e26 FLOPS
#     R4 (bimonthly):    10/22  → 12/22*  parameters 1.746T → 2.194e26 FLOPS
#     R5 (future):       12/22  →  …      parameters 1.899T → 2.535e26 FLOPS
# * R4 release date falls just past the horizon end (12/1/2026); R5 is
#   entirely outside the horizon.
PLANNING_DOC_RELEASES_FLOPS = [
    ("R1", date(2026,  6,  1), date(2026,  6, 22), 1.30957574741e26),
    ("R2", date(2026,  6, 22), date(2026,  8, 22), 1.41269312142e26),
    ("R3", date(2026,  8, 22), date(2026, 10, 22), 1.76061533097e26),
    ("R4", date(2026, 10, 22), date(2026, 12, 22), 2.19422484389e26),
    # R5 omitted — fully outside the horizon
]

# FLOPS-per-MWh derived from the hardware spec above. Per site:
#   GPUs × (SXM_share × SXM_TF/s + PCIe_share × PCIe_TF/s) × 1e12 → FLOPS/s
#   × 3600 → FLOPS/hr  ÷ SITE_COMPUTE_CAPACITY_MW → FLOPS per compute-MWh
def flops_per_compute_mwh(sxm_fraction: float = SXM_FRACTION_DEFAULT) -> float:
    pcie = 1.0 - sxm_fraction
    tf_per_sec_per_gpu = (
        sxm_fraction * H100_SXM_SUSTAINED_TFLOPS_PER_SEC
        + pcie       * H100_PCIE_SUSTAINED_TFLOPS_PER_SEC
    )
    flops_per_sec_per_site = GPUS_PER_SITE * tf_per_sec_per_gpu * 1e12
    flops_per_hr_per_site  = flops_per_sec_per_site * 3600.0
    return flops_per_hr_per_site / SITE_COMPUTE_CAPACITY_MW

FLOPS_PER_COMPUTE_MWH = flops_per_compute_mwh()

# Total system-wide teraFLOPS/hour cap derived directly from the hardware
# spec — useful for sanity-checking and for computing the minimum feasible
# cadence (the LP's `train + inf ≤ SITE_POWER_CAPACITY_MW` constraint is
# the same cap expressed in grid-MWh).
def total_tflops_per_hour(sxm_fraction: float = SXM_FRACTION_DEFAULT) -> float:
    """Aggregate sustained teraFLOPS/hour across BOTH sites at 100% compute.
    Equivalent to FLOPS_PER_COMPUTE_MWH × (2 sites × 80 cMWh) ÷ 1e12."""
    return flops_per_compute_mwh(sxm_fraction) * 2 * SITE_COMPUTE_CAPACITY_MW / 1e12


def min_feasible_cadence_days(release_date: date,
                              sxm_fraction: float = SXM_FRACTION_DEFAULT) -> float:
    """The cadence below which a release of size `project_compute_mwh(...)`
    can't fit in its window even at 100% compute. = compute / max_per_day."""
    cmwh = project_compute_mwh(release_date, sxm_fraction)
    max_per_day = 2 * SITE_COMPUTE_CAPACITY_MW * 24.0   # both sites, 24 h
    return cmwh / max_per_day


# ── Token-price decay (planning doc) ──────────────────────────────────────
# Planning doc: "token costs (for the consumer) seem to be halving every
# couple of months (revenue per token dropping)". We model frontier-tier
# revenue per token as halving every TOKEN_PRICE_HALFLIFE_DAYS days SINCE
# THE LAST RELEASE. Each new model release resets the clock back to peak.
# At horizon start we assume the operator's deployed model is frontier
# (t-since-release = 0 ⇒ no decay applied at hour 0).
TOKEN_PRICE_HALFLIFE_DAYS = 60.0


@dataclass
class TrainingRun:
    """One model release: a contiguous training window with a compute floor."""
    name: str
    window_start: date       # earliest hour that may run training for this release
    release_date: date       # at this date, the model is live (= compute floor met)
    compute_mwh_required: float   # compute-MWh (NOT grid-MWh) that must be spent
                                  # on this run before release_date
    token_revenue_multiplier: float = 1.0
        # ^ scales inference revenue while THIS release is the deployed model.
        # Captures generation-over-generation quality uplift OR market-side
        # token-price differences. The default 1.0 means "no uplift; just
        # decay since release determines revenue".
    is_initial: bool = False
        # ^ if True, the LP forbids inference during this run's window
        # (100% compute → training, per RFP / user spec for the initial model).

    @property
    def grid_mwh_required(self) -> float:
        return self.compute_mwh_required * PUE


# ── Parameter & FLOPS projection (Epoch AI regressions) ──────────────────
# Fits computed in fit_growth_curves.py from the two CSVs the planning doc
# references:
#   (1) artificial-intelligence-parameter-count.csv
#       Three filter regimes computed; we use POST-2020 (closest match
#       to the planning doc's stated R1-R5 numerical values once the 5×
#       competitiveness multiplier is applied):
#         post-2020: log10(params)   = -49.6585 + 1.3204e-3 · day_serial
#                    n=395, R²=0.30, doubling ≈ 228 days
#                    @ 6/1/2026 with 5× → 1.02e12 params (vs doc's 1.29e12)
#       Other regimes available in fit_growth_curves.py:
#         post-2010: intercept -31.7005, slope 9.2089e-4 (R²=0.50)
#                    @ 6/1/2026 with 5× → 3.31e11 params (much smaller)
#         post-2018: intercept -45.1286, slope 1.2203e-3 (R²=0.39)
#                    @ 6/1/2026 with 5× → 8.23e11 params
#   (2) ai-training-computation-vs-parameters-by-researcher-affiliation.csv
#       log10(petaFLOPS)      = -9.8192 + 1.7187 · log10(params)
#       R² = 0.84,  power-law exponent 1.72 (Chinchilla-like)
PARAM_FIT_INTERCEPT_LOG10     = -49.658518
PARAM_FIT_SLOPE_LOG10_PER_DAY =   0.00132043
FLOPS_FIT_INTERCEPT_LOG10           = -9.8192   # in petaFLOPS
FLOPS_FIT_SLOPE_LOG10_PER_LOG10_P   =  1.7187

# Excel serial-date epoch — used by both CSVs
EXCEL_EPOCH = date(1899, 12, 30)
def excel_serial(d: date) -> int:
    return (d - EXCEL_EPOCH).days

# Planning doc: "we will use a 5× multiplier on our model" — the Epoch AI
# dataset cuts off at ~2023, but we're targeting 2026 frontier-class
# competitors (DeepSeek 1.6T, Xiaomi 1.02T, ChatGPT-4 1.7T+). The 5×
# multiplier bridges the gap between the regression line (which captures
# the average researcher, including all the small academic releases that
# pull the trend down) and the actual frontier where we have to compete.
PARAM_COMPETITIVENESS_MULTIPLIER = 5.0


# NOTE on which date to feed in: the planning doc uses the TRAINING START
# DATE (i.e., the date you decide what model size to build and begin the
# run), not the eventual release date. The doc's own R1-R5 table is keyed
# off 6/1, 6/22, 8/22, 10/22, 12/22 — those are the *start-of-training*
# dates, even though the model goes live one window later.
def project_params(training_start_date: date) -> float:
    """Projected param count for a model whose training STARTS on this date,
    with the planning doc's 5× competitiveness multiplier applied."""
    log10_p = (PARAM_FIT_INTERCEPT_LOG10
               + PARAM_FIT_SLOPE_LOG10_PER_DAY * excel_serial(training_start_date))
    return (10.0 ** log10_p) * PARAM_COMPETITIVENESS_MULTIPLIER


def project_petaflops(training_start_date: date) -> float:
    """Training compute (petaFLOPS) required, derived from
    params(training_start_date) → FLOPS(params)."""
    p = project_params(training_start_date)
    log10_pf = (FLOPS_FIT_INTERCEPT_LOG10
                + FLOPS_FIT_SLOPE_LOG10_PER_LOG10_P * math.log10(p))
    return 10.0 ** log10_pf


def project_flops(training_start_date: date) -> float:
    return project_petaflops(training_start_date) * 1e15


def project_compute_mwh(training_start_date: date,
                        sxm_fraction: float = SXM_FRACTION_DEFAULT) -> float:
    """Compute-MWh required to train a model whose training STARTS on
    `training_start_date`. The chain is:
        training_start_date  →  params (5× multiplier)
        params               →  petaFLOPS (Epoch AI power-law fit)
        petaFLOPS            →  compute-MWh (÷ FLOPS_PER_COMPUTE_MWH)
    """
    return project_flops(training_start_date) / flops_per_compute_mwh(sxm_fraction)


@dataclass
class TrainingSchedule:
    """Ordered list of TrainingRuns over the horizon."""
    name: str
    runs: List[TrainingRun] = field(default_factory=list)

    @property
    def release_dates(self) -> List[date]:
        return [r.release_date for r in self.runs]

    @property
    def total_compute_mwh(self) -> float:
        return sum(r.compute_mwh_required for r in self.runs)


def _initial_R1_duration_days(sxm_fraction: float = SXM_FRACTION_DEFAULT) -> int:
    """Days needed to complete R1 training at 100% compute on BOTH sites.

    The user spec: "the initial model release (training started on June 1st)
    will assume 100% compute used for training the model, so it should take
    less time for that than the usual training schedule". So R1's window
    length is whatever the projected compute requirement says — at full
    160 MW-compute/hour usage."""
    req = project_compute_mwh(HORIZON_START, sxm_fraction)
    max_per_day = 2 * SITE_COMPUTE_CAPACITY_MW * 24.0   # both sites, 24h
    return max(1, math.ceil(req / max_per_day))


def _per_release_multipliers(release_dates: List[date],
                             scheme: str,
                             *,
                             uplift_factor: float = 1.5,
                             halflife_days: float = TOKEN_PRICE_HALFLIFE_DAYS
                            ) -> List[float]:
    """Build per-release token-revenue multipliers.

    scheme:
      'constant'       all multipliers = 1.0 (decay alone drives non-degeneracy)
      'quality_uplift' multiplier_k = uplift_factor**k  (newer = better model)
      'market_decay'   multiplier_k = 0.5**(t_days/halflife)  (consumer prices fall)
      'doc_blended'    quality_uplift × market_decay (planning doc's net story)
    """
    mults = []
    horizon_start = HORIZON_START
    for k, rd in enumerate(release_dates, start=1):
        t = (rd - horizon_start).days
        if scheme == "constant":
            mults.append(1.0)
        elif scheme == "quality_uplift":
            mults.append(uplift_factor ** k)
        elif scheme == "market_decay":
            mults.append(0.5 ** (t / halflife_days))
        elif scheme == "doc_blended":
            mults.append((uplift_factor ** k) * (0.5 ** (t / halflife_days)))
        else:
            raise ValueError(f"unknown multiplier scheme: {scheme!r}")
    return mults


def planning_doc_schedule(horizon_end: date = HORIZON_END,
                          sxm_fraction: float = SXM_FRACTION_DEFAULT,
                          token_multiplier_scheme: str = "constant",
                          uplift_factor: float = 1.5,
                          ) -> TrainingSchedule:
    """Planning-doc-style bimonthly schedule.

    All release dates derive from the rule:
        R1 starts 6/1 and ends when its 100%-compute requirement is met
        R(k+1) start  =  R(k) end  =  R(k) release date
        R(k+1) length =  60 days   (planning doc's "every 2 months")

    The doc's literal calendar dates (R2=8/22, R3=10/22, R4=12/22) only
    hold under the doc's assumed 21-day R1 — at smaller param projections
    R1 finishes sooner, which slides every subsequent release earlier in
    lock-step.
    """
    sch = equal_cadence_schedule(
        period_days=60,
        horizon_end=horizon_end,
        sxm_fraction=sxm_fraction,
        token_multiplier_scheme=token_multiplier_scheme,
        uplift_factor=uplift_factor,
    )
    sch.name = f"planning_doc_bimonthly_{token_multiplier_scheme}"
    return sch


def equal_cadence_schedule(period_days: int,
                           horizon_start: date = HORIZON_START,
                           horizon_end:   date = HORIZON_END,
                           sxm_fraction:  float = SXM_FRACTION_DEFAULT,
                           token_multiplier_scheme: str = "constant",
                           uplift_factor: float = 1.5,
                          ) -> TrainingSchedule:
    """Generate a cadence schedule. R1 always 100% compute, ending after
    R1's required training time. R2+ spaced every `period_days` after R1,
    with compute requirements projected from each release date.

    Trailing partial windows keep their true release date (past horizon)
    so the revenue decay path doesn't get a spurious reset.
    """
    # R1: initial, 100% compute, short
    r1_release = horizon_start + timedelta(
        days=_initial_R1_duration_days(sxm_fraction)
    )
    if r1_release >= horizon_end:
        return TrainingSchedule(name=f"every_{period_days}d",
                                runs=[TrainingRun("R1", horizon_start, r1_release,
                                                  project_compute_mwh(horizon_start, sxm_fraction),
                                                  token_revenue_multiplier=1.0,
                                                  is_initial=True)])
    # R2, R3, … at `period_days` intervals starting from R1's release.
    release_dates = [r1_release]
    window_starts = [horizon_start]
    cur = r1_release
    while cur < horizon_end:
        nxt = cur + timedelta(days=period_days)
        window_starts.append(cur)
        release_dates.append(nxt)
        cur = nxt
    multipliers = _per_release_multipliers(release_dates, token_multiplier_scheme,
                                           uplift_factor=uplift_factor)
    runs = []
    for k, (ws, rd, mult) in enumerate(zip(window_starts, release_dates, multipliers),
                                       start=1):
        # Compute requirement is keyed off the training START date (ws),
        # following the planning doc's methodology.
        compute = project_compute_mwh(ws, sxm_fraction)
        if rd > horizon_end:
            in_h = max((horizon_end - ws).days, 0)
            tot  = (rd - ws).days
            compute *= in_h / tot if tot > 0 else 0.0
        runs.append(TrainingRun(
            name=f"R{k}",
            window_start=ws,
            release_date=rd,
            compute_mwh_required=compute,
            token_revenue_multiplier=mult,
            is_initial=(k == 1),
        ))
    return TrainingSchedule(name=f"every_{period_days}d_{token_multiplier_scheme}",
                            runs=runs)


def no_training_schedule() -> TrainingSchedule:
    """No releases at all — revenue decays continuously from horizon start."""
    return TrainingSchedule(name="no_training", runs=[])


def cadence_passes_500_floor(cadence_days: int,
                             sxm_fraction: float = SXM_FRACTION_DEFAULT,
                             min_grid_mwh_per_day: float = 500.0,
                             max_grid_mwh_per_day: float | None = None
                             ) -> bool:
    """Check that this cadence is both
      - ≥ `min_grid_mwh_per_day` of natural training (per-release amortized)
        — so the LP doesn't have to pad with the RFP floor; AND
      - ≤ `max_grid_mwh_per_day` — i.e. every release window's compute
        requirement fits inside the data centers' grid-power capacity.

    R2 is the smallest non-initial release (governs the 500/day check);
    the last full release before horizon end is the largest (governs the
    feasibility upper bound).
    """
    if max_grid_mwh_per_day is None:
        # Both sites at full 100-MWh/hr grid draw, 24 hours per day:
        max_grid_mwh_per_day = 2 * SITE_POWER_CAPACITY_MW * 24.0
    sch = equal_cadence_schedule(cadence_days,
                                 sxm_fraction=sxm_fraction,
                                 token_multiplier_scheme="constant")
    rates = []
    for run in sch.runs:
        if run.is_initial:
            continue
        # The LP can only train during in-horizon hours. For runs whose
        # release_date extends past horizon end, compute_mwh_required is
        # already pro-rated; pair it with the in-horizon window length.
        end_in_horizon = min(run.release_date, HORIZON_END)
        days = max((end_in_horizon - run.window_start).days, 0)
        if days <= 0:
            continue
        rates.append(run.grid_mwh_required / days)
    if not rates:
        return True
    if min(rates) < min_grid_mwh_per_day:
        return False
    if max(rates) > max_grid_mwh_per_day:
        return False
    return True


def refinement_cadences(winner_days: int,
                        n: int = 6,
                        frac: float = 0.30,
                        sxm_fraction: float = SXM_FRACTION_DEFAULT
                        ) -> List[int]:
    """Generate `n` integer cadences within ±frac of `winner_days`, deduped,
    filtered to those passing the 500 MWh/day floor."""
    if winner_days <= 0:
        return []
    lo = max(1, int(round(winner_days * (1 - frac))))
    hi = max(lo + n, int(round(winner_days * (1 + frac))))
    import numpy as _np
    raw = _np.linspace(lo, hi, n).round().astype(int).tolist()
    deduped = sorted(set(raw))
    return [c for c in deduped if cadence_passes_500_floor(c, sxm_fraction)]


# ── Scenario flags ─────────────────────────────────────────────────────────
@dataclass
class Scenario:
    """Tunable scenario inputs. Defaults = LMP-only, no tolling, no BESS.

    Procurement-side flags:
      * use_houston_tolling — Houston ONLY (RFP: no gas plant in West)
      * use_bess            — battery storage; applies at BOTH sites by
                              default. Pass `bess_sites=("HOUSTON",)` or
                              `("WEST",)` to test single-site BESS.
    """
    use_houston_tolling: bool = False
    use_bess: bool            = False
    bess_sites: tuple         = field(default_factory=lambda: SITES)  # default: both sites
    # Allow re-pricing via CLI without editing this file:
    token_input_price_per_mm:  float = TOKEN_PRICE_INPUT_PER_MM
    token_output_price_per_mm: float = TOKEN_PRICE_OUTPUT_PER_MM
    # Mandatory RFP daily training floor (grid-MWh per day, system-total).
    # Default 500.0 = the RFP-specified minimum. The cadence filter
    # (cadence_passes_500_floor) ensures all candidate cadences naturally
    # exceed this rate, so the constraint is non-binding for valid cadences
    # but enforces compliance for edge cases (e.g., no_training schedule).
    training_min_mwh_per_day:  float = 500.0

    def inference_rev_per_grid_mwh(self) -> float:
        blended = (
            INPUT_REVENUE_FRACTION  * self.token_input_price_per_mm
            + OUTPUT_REVENUE_FRACTION * self.token_output_price_per_mm
        )
        per_compute_mwh = TOKENS_PER_COMPUTE_MWH * blended / 1e6
        return per_compute_mwh / PUE


if __name__ == "__main__":
    s = Scenario()
    print(f"Tokens / compute-MWh        : {TOKENS_PER_COMPUTE_MWH:,.0f}")
    print(f"Blended token revenue $/MM  : {TOKEN_REVENUE_PER_MM:,.2f}")
    print(f"Inference rev $/compute-MWh : {INFERENCE_REV_PER_COMPUTE_MWH:,.2f}")
    print(f"Inference rev $/grid-MWh    : {INFERENCE_REV_PER_GRID_MWH:,.2f}")
    print(f"Tolling cost @ $3 HH gas    : ${tolling_cost_per_mwh(3.0):,.2f}/MWh")
    print(f"BESS 6-mo lease cost / site : ${BESS_6MO_LEASE_COST:,.0f}")
