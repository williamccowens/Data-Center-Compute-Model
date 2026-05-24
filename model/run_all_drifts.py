"""
Run the headline + sweep + post-processing pipeline for every committed
drift scenario, writing each into its own snapshot folder under
`example_outputs_TEMPORARY/`. This is the "reproduce everything" entry
point — `python model/run_all_drifts.py`.

For each drift scenario, in order:

  1. `python model/run_planning_doc.py --mc N --gas-drift-pct X --power-drift-pct Y`
     — Phases A / B / C, verification, final hourly schedule, the
     baseline figs 01–04 + 05/06/07/08 (multi-K), per_k hourly re-solve.
  2. `python model/power_procurement_sweep.py --mc N --toll-cap-sweep
     --gas-drift-pct X --power-drift-pct Y` — 8-scenario procurement
     ablation + virtual BESS TBx + toll daily-cap sweep + reservation +
     capacity-payment sweeps.
  3. Copy the `model/outputs/` contents into the per-scenario snapshot
     folder.
  4. `python model/render_tables.py <snapshot>` — RESULTS_TABLES.{md,html}.
  5. (per_k_hourly artifacts are produced by step 1 inside outputs/, so
     they get carried over by step 3.)

After all four scenarios, runs
  6. `python model/compare_snapshots.py` — SNAPSHOT_COMPARISON.{md,html}
     + comparison_figures/.
  7. `python model/variable_cost_snapshot.py` — 5th 'variable-cost view'
     snapshot showing Phase A/B's pre-lease LP profits.

End-state: every artifact in `example_outputs_TEMPORARY/` is rebuilt
from scratch under the current model code.

Each step writes its console output to `<snapshot>/headline_stdout.log`
or `<snapshot>/sweep_stdout.log` so individual runs are debuggable.

Estimated wall-clock at --mc 50 on 11 cores:
  ~25 min planning doc + ~10 min procurement sweep per scenario, × 4
  scenarios + ~2 min post-processing = ~2.5 hours total.

Run:
    python model/run_all_drifts.py              # default --mc 50
    python model/run_all_drifts.py --mc 10      # quick smoke test
    python model/run_all_drifts.py --skip ai_plus_brent  # subset
"""
from __future__ import annotations
import sys
import argparse
import shutil
import subprocess
import time
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR    = PROJECT_ROOT / "model"
OUTPUTS_DIR  = MODEL_DIR / "outputs"
SNAPS_PARENT = PROJECT_ROOT / "example_outputs_TEMPORARY"


# Drift configurations — must mirror the labels and gas/power overlays
# documented in each snapshot's INDEX.md. Add new scenarios here.
DRIFT_SCENARIOS = {
    "baseline":      {"gas": 0.000, "power": 0.000,
                      "desc": "EIA STEO May-2026 short-term view (flat 2025->2026)"},
    "ai_structural": {"gas": 0.005, "power": 0.010,
                      "desc": "EIA AEO + ERCOT CDR secular load-growth"},
    "mild_drift":    {"gas": 0.030, "power": 0.015,
                      "desc": "~half geopolitical Brent shock overlay"},
    "ai_plus_brent": {"gas": 0.065, "power": 0.040,
                      "desc": "Structural + full +30% Brent shock (max stress)"},
}


def _snapshot_dir(label: str, mc: int) -> Path:
    today = date.today().isoformat()
    return SNAPS_PARENT / f"run_n{mc}_{today}_{label}"


def _run_cmd(cmd: list[str], log_path: Path, env: dict | None = None) -> int:
    """Run `cmd` (no shell), tee stdout/stderr to `log_path`, return rc."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  $ {' '.join(cmd)}", flush=True)
    print(f"    (log -> {log_path})", flush=True)
    with open(log_path, "w", encoding="utf-8", errors="replace") as f:
        proc = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env,
                              stdout=f, stderr=subprocess.STDOUT)
    return proc.returncode


def _copy_outputs(snapshot_dir: Path) -> None:
    """Copy everything currently in model/outputs/ into the snapshot dir,
    overwriting any prior content."""
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for item in OUTPUTS_DIR.iterdir():
        dst = snapshot_dir / item.name
        if item.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def _clean_outputs() -> None:
    """Empty the working outputs dir between scenarios so we don't carry
    stale figures / CSVs from a previous drift into the next snapshot."""
    if not OUTPUTS_DIR.exists():
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        return
    for item in OUTPUTS_DIR.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def run_one(label: str, gas: float, power: float, mc: int,
             skip_sweep: bool = False) -> Path:
    """Run the headline + sweep pipeline for one drift scenario.
    Returns the snapshot directory."""
    print(f"\n{'='*78}\nSCENARIO: {label}  (gas {gas:+.1%}, power {power:+.1%})\n{'='*78}")
    snapshot = _snapshot_dir(label, mc)
    snapshot.mkdir(parents=True, exist_ok=True)

    _clean_outputs()

    headline_cmd = [
        sys.executable, "-X", "utf8", str(MODEL_DIR / "run_planning_doc.py"),
        "--mc", str(mc),
        "--gas-drift-pct",   str(gas),
        "--power-drift-pct", str(power),
    ]
    rc = _run_cmd(headline_cmd, snapshot / "headline_stdout.log")
    if rc != 0:
        print(f"  X planning_doc failed (rc={rc}); see log")
        return snapshot

    if not skip_sweep:
        sweep_cmd = [
            sys.executable, "-X", "utf8",
            str(MODEL_DIR / "power_procurement_sweep.py"),
            "--mc", str(mc),
            "--toll-cap-sweep",
            "--reservation-sweep",
            "--capacity-payment-sweep",
            "--gas-drift-pct",   str(gas),
            "--power-drift-pct", str(power),
        ]
        rc = _run_cmd(sweep_cmd, snapshot / "sweep_stdout.log")
        if rc != 0:
            print(f"  X power_procurement_sweep failed (rc={rc}); see log")

    _copy_outputs(snapshot)

    # Render the per-snapshot tables + auto-tables in INDEX.md (if INDEX
    # is present from a previous run; otherwise harmless).
    _run_cmd([sys.executable, "-X", "utf8",
              str(MODEL_DIR / "render_tables.py"), str(snapshot)],
              snapshot / "render_tables_stdout.log")
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mc", type=int, default=50,
                        help="MC paths per scenario (default 50).")
    parser.add_argument("--skip", default="",
                        help="Comma-separated scenarios to skip "
                             f"(any of: {', '.join(DRIFT_SCENARIOS)}).")
    parser.add_argument("--only", default="",
                        help="Comma-separated scenarios to run "
                             "(others skipped).")
    parser.add_argument("--no-sweep", action="store_true",
                        help="Skip power_procurement_sweep step (headline only).")
    parser.add_argument("--skip-comparison", action="store_true",
                        help="Skip cross-snapshot comparison + variable-cost "
                             "snapshot at the end.")
    args = parser.parse_args()

    skip = {s.strip() for s in args.skip.split(",") if s.strip()}
    only = {s.strip() for s in args.only.split(",") if s.strip()}
    scenarios = [(label, cfg["gas"], cfg["power"])
                 for label, cfg in DRIFT_SCENARIOS.items()
                 if label not in skip and (not only or label in only)]
    if not scenarios:
        print("No scenarios to run (check --skip / --only).")
        return

    print(f"Running {len(scenarios)} drift scenarios at --mc {args.mc} ...")
    t0 = time.time()
    snapshots = []
    for label, gas, power in scenarios:
        snap = run_one(label, gas, power, args.mc, skip_sweep=args.no_sweep)
        snapshots.append(snap)
    print(f"\nAll scenarios complete in {(time.time()-t0)/60:.1f} min.")

    if not args.skip_comparison:
        print(f"\n{'='*78}\nCROSS-SNAPSHOT COMPARISON\n{'='*78}")
        _run_cmd([sys.executable, "-X", "utf8",
                  str(MODEL_DIR / "compare_snapshots.py")],
                  SNAPS_PARENT / "compare_snapshots_stdout.log")
        print(f"\n{'='*78}\nVARIABLE-COST SNAPSHOT (Phase A/B pre-lease view)\n{'='*78}")
        baseline_snap = _snapshot_dir("baseline", args.mc)
        if baseline_snap.exists():
            _run_cmd([sys.executable, "-X", "utf8",
                      str(MODEL_DIR / "variable_cost_snapshot.py"),
                      str(baseline_snap)],
                      SNAPS_PARENT / "variable_cost_stdout.log")
        else:
            print(f"  X baseline snapshot {baseline_snap.name} not found; "
                  "skipping variable-cost snapshot.")

    print("\nDone. Inspect SNAPSHOT_COMPARISON.{md,html} for the cross-snapshot view.")


if __name__ == "__main__":
    sys.exit(main() or 0)
