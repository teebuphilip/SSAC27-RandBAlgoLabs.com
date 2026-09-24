#!/usr/bin/env python3
"""Bootstrap uncertainty intervals for the Sloan roster-score comparison."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
TEAM_OPS_PATH = RESULTS_DIR / "comparison_summary_sanitized.json"
OUTCOME_PATH = RESULTS_DIR / "team_season_outcomes.csv"


def _auc(y: np.ndarray, score: np.ndarray) -> float:
    order = np.argsort(score, kind="mergesort")
    ranked = np.empty(len(score), dtype=float)
    ranked[order] = np.arange(1, len(score) + 1, dtype=float)
    positive = y.astype(bool)
    n_positive = int(positive.sum())
    n_negative = int((~positive).sum())
    if not n_positive or not n_negative:
        return float("nan")
    return float((ranked[positive].sum() - n_positive * (n_positive + 1) / 2) / (n_positive * n_negative))


def _load_frame() -> pd.DataFrame:
    payload = json.loads(TEAM_OPS_PATH.read_text(encoding="utf-8"))
    team_values = pd.DataFrame(payload["team_ops_backtest"]["team_values"])
    outcomes = pd.read_csv(OUTCOME_PATH)[
        ["season", "team", "made_conf_finals", "made_finals", "won_championship"]
    ].drop_duplicates(["season", "team"])
    frame = team_values.merge(outcomes, on=["season", "team"], how="inner")
    frame["season_start"] = frame["season"].astype(str).str.slice(0, 4).astype(int)
    return frame


def _bootstrap(frame: pd.DataFrame, score_col: str, outcome_col: str, *, iterations: int, seed: int) -> dict[str, float | int | str]:
    clean = frame[[score_col, outcome_col]].dropna().copy()
    y = clean[outcome_col].astype(bool).to_numpy()
    scores = clean[score_col].astype(float).to_numpy()
    rng = np.random.default_rng(seed)
    estimates: list[float] = []
    for _ in range(iterations):
        sample = rng.integers(0, len(clean), len(clean))
        estimate = _auc(y[sample], scores[sample])
        if not np.isnan(estimate):
            estimates.append(estimate)
    values = np.asarray(estimates, dtype=float)
    return {
        "score": score_col,
        "outcome": outcome_col,
        "rows": int(len(clean)),
        "positive_rate": float(y.mean()),
        "auc": _auc(y, scores),
        "ci_low": float(np.quantile(values, 0.025)),
        "ci_high": float(np.quantile(values, 0.975)),
        "bootstrap_iterations": int(len(values)),
    }


def build_report(*, output_md: Path, output_json: Path, iterations: int = 2000, seed: int = 20270914) -> dict[str, object]:
    frame = _load_frame()
    rows = []
    for window, subset in [("1995-2025", frame), ("2013-2025", frame[frame["season_start"] >= 2013].copy())]:
        for score in ["team_total_score", "team_rate_score", "wins"]:
            for outcome in ["made_conf_finals", "made_finals", "won_championship"]:
                result = _bootstrap(subset, score, outcome, iterations=iterations, seed=seed)
                result["window"] = window
                rows.append(result)

    payload = {"rows": rows, "source_rows": int(len(frame)), "iterations_requested": iterations, "seed": seed}
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Sloan Bootstrap Uncertainty Check",
        "",
        "This note uses row-resampled bootstrap intervals for AUC. It is an uncertainty check around the fixed score comparison, not a new tuning pass. The score definitions and outcome labels are unchanged.",
        "",
        f"Bootstrap iterations: {iterations}; seed: {seed}.",
        "",
        "| Window | Score | Outcome | Rows | Base rate | AUC | 95% interval |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| {row['window']} | {row['score']} | {row['outcome']} | {row['rows']} | "
            f"{row['positive_rate']:.1%} | {row['auc']:.1%} | {row['ci_low']:.1%}-{row['ci_high']:.1%} |"
        )
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output-md", default=str(RESULTS_DIR / "bootstrap-uncertainty.md"))
    parser.add_argument("--output-json", default=str(RESULTS_DIR / "bootstrap-uncertainty.json"))
    args = parser.parse_args()
    build_report(
        output_md=Path(args.output_md),
        output_json=Path(args.output_json),
        iterations=args.iterations,
    )
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
