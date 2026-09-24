#!/usr/bin/env python3
"""Run the Sloan comparison that turns archetype shape into a real evaluation.

This script compares offense-only, defense-only, and combined two-way roster-shape
signals against simple baselines. The main comparison window is the modern overlap
period where offense, defense, and combined layers all exist. A separate offense-only
appendix table is also written for the full historical archive.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SLOAN_DIR = PROJECT_ROOT / "sloan2027"

OFFENSE_TEAM_PATH = PROJECT_ROOT / "reports" / "backtests" / "team_archetype_study" / "team_season_archetype_mixes.csv"
OFFENSE_PLAYER_PATH = PROJECT_ROOT / "reports" / "backtests" / "team_archetype_study" / "top_players_with_archetypes.csv"
OFFENSE_CLUSTER_SUMMARY_PATH = PROJECT_ROOT / "output" / "clusters" / "cluster_summary.csv"
DEFENSE_TEAM_PATH = PROJECT_ROOT / "reports" / "backtests" / "defensive_archetype_study" / "team_season_offense_defense_mixes.csv"
DEFENSE_PLAYER_PATH = PROJECT_ROOT / "reports" / "backtests" / "defensive_archetype_study" / "player_offense_defense_combined_archetypes_modern.csv"
DEFENSE_TRACKING_SCORDED_PATH = PROJECT_ROOT / "data" / "comps" / "advanced_defense" / "player_defense_tracking_scored.csv"
DEFENSE_CLUSTER_SUMMARY_PATH = PROJECT_ROOT / "reports" / "roster_construction" / "advanced_defense_archetypes" / "defense_cluster_summary.csv"
FMVW_TEAM_PATH = PROJECT_ROOT / "reports" / "basketball_ops" / "fmvw_backtest" / "fmvw_backtest_team_values.csv"
TEAM_OPS_COMPARISON_PATH = PROJECT_ROOT / "reports" / "basketball_ops" / "comparisons" / "comparison_summary.json"

OFFENSE_PAIR_PATH = PROJECT_ROOT / "reports" / "backtests" / "team_archetype_study" / "archetype_pair_postseason_outcomes.csv"
DEFENSE_PAIR_PATH = PROJECT_ROOT / "reports" / "backtests" / "defensive_archetype_study" / "defense_archetype_pair_postseason_outcomes.csv"
COMBINED_PAIR_PATH = PROJECT_ROOT / "reports" / "backtests" / "defensive_archetype_study" / "combined_archetype_pair_postseason_outcomes.csv"

DEFAULT_ALPHA = 10.0
# The Sloan task board locks conference-finals appearance as the primary
# outcome.  ``made_conf_semis`` is a distinct earlier-round outcome derived
# from one playoff-series win; using it here silently tested the wrong target.
PRIMARY_OUTCOME = "made_conf_finals"
SOFTMAX_TEMPERATURE = 0.75
OFFENSE_SOFT_TEMPERATURE_SWEEP = [0.5, 0.65, 0.75]

OFFENSE_SOFT_FEATURES = [
    "PTS",
    "REB",
    "AST",
    "STL",
    "BLK",
    "TO",
    "FG_PCT",
    "FT_PCT",
    "THREE_PM",
]

DEFENSE_SOFT_FEATURES = [
    "overall_defense_score_raw_z",
    "rim_protection_score_raw_z",
    "perimeter_defense_score_raw_z",
]


@dataclass(frozen=True)
class LayerConfig:
    name: str
    frame: pd.DataFrame
    set_col: str
    window_label: str
    era_bounds: list[tuple[str, int, int]]
    pair_path: Path


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return pd.read_csv(path)


def _season_start(season: str) -> int:
    return int(str(season).split("-")[0])


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _attach_targets(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if "playoff_series_wins" in result.columns and PRIMARY_OUTCOME not in result.columns:
        result[PRIMARY_OUTCOME] = result["playoff_series_wins"].fillna(0).astype(int) >= 1
    return result


def _assign_era(season: str, bounds: list[tuple[str, int, int]]) -> str | None:
    year = _season_start(season)
    for label, start, end in bounds:
        if start <= year <= end:
            return label
    return None


def _normalize_token_list(value: str) -> list[str]:
    tokens = []
    for item in str(value).split(" + "):
        item = item.strip()
        if item and item != "UNKNOWN":
            tokens.append(item)
    # Keep deterministic ordering and remove duplicates.
    return sorted(set(tokens))


def _single_token(value: object) -> str | None:
    token = str(value).strip()
    if not token or token == "UNKNOWN" or token == "nan":
        return None
    return token


def _numeric_vector(row: pd.Series, feature_cols: list[str]) -> np.ndarray:
    return np.array([_safe_float(row.get(col), 0.0) for col in feature_cols], dtype=float)


def _softmax_probabilities(distances: np.ndarray, temperature: float = SOFTMAX_TEMPERATURE) -> np.ndarray:
    if len(distances) == 0:
        return np.array([], dtype=float)
    temp = max(float(temperature), 1e-6)
    logits = -distances / temp
    logits -= float(np.max(logits))
    weights = np.exp(logits)
    total = float(weights.sum())
    if total <= 0:
        return np.full(len(distances), 1.0 / len(distances), dtype=float)
    return weights / total


def _cluster_centroid_table(
    frame: pd.DataFrame,
    *,
    feature_cols: list[str],
    position_col: str = "position",
    cluster_col: str = "cluster_id",
) -> dict[str, dict[str, object]]:
    if frame.empty:
        return {}

    available_features = [col for col in feature_cols if col in frame.columns]
    if not available_features:
        raise ValueError("No usable feature columns available for cluster probability scoring.")

    centroid_table: dict[str, dict[str, object]] = {}
    for position, group in frame.groupby(position_col):
        clean = group.copy()
        for col in available_features:
            clean[col] = pd.to_numeric(clean[col], errors="coerce").fillna(0.0)
        matrix = clean[available_features].to_numpy(dtype=float)
        scale = matrix.std(axis=0)
        scale = np.where(scale == 0, 1.0, scale)
        centroid_table[str(position)] = {
            "cluster_ids": clean[cluster_col].astype(str).tolist(),
            "centroids": matrix,
            "scale": scale,
            "feature_cols": available_features,
        }
    return centroid_table


def _nearest_cluster_probabilities(
    row: pd.Series,
    centroid_table: dict[str, dict[str, object]],
    *,
    position_col: str,
    temperature: float = SOFTMAX_TEMPERATURE,
) -> dict[str, float]:
    position = _single_token(row.get(position_col))
    if position is None or position not in centroid_table:
        return {}

    info = centroid_table[position]
    feature_cols = list(info["feature_cols"])
    centroids = np.asarray(info["centroids"], dtype=float)
    scale = np.asarray(info["scale"], dtype=float)
    if centroids.size == 0:
        return {}

    player_vec = _numeric_vector(row, feature_cols)
    distances = np.linalg.norm((centroids - player_vec) / scale, axis=1)
    probs = _softmax_probabilities(distances, temperature=temperature)
    return {cluster_id: float(prob) for cluster_id, prob in zip(info["cluster_ids"], probs)}


def _build_probability_frame(
    frame: pd.DataFrame,
    *,
    cluster_summary_path: Path,
    feature_cols: list[str],
    position_col: str,
    probability_label: str,
    temperature: float = SOFTMAX_TEMPERATURE,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()

    centroid_table = _cluster_centroid_table(
        _read_csv(cluster_summary_path),
        feature_cols=feature_cols,
        position_col="position",
        cluster_col="cluster_id",
    )
    rows = []
    for _, row in frame.iterrows():
        probabilities = _nearest_cluster_probabilities(
            row,
            centroid_table,
            position_col=position_col,
            temperature=temperature,
        )
        if not probabilities:
            continue
        rows.append(
            {
                "season": str(row["season"]),
                "team": str(row["team"]),
                "player_id": str(row["player_id"]),
                "player_name": str(row.get("player_name", "")),
                "position": str(row.get(position_col, row.get("position", ""))),
                probability_label: probabilities,
            }
        )
    return pd.DataFrame(rows)


def _build_joint_probability_frame(
    offense_probs: pd.DataFrame,
    defense_probs: pd.DataFrame,
) -> pd.DataFrame:
    if offense_probs.empty or defense_probs.empty:
        return pd.DataFrame()

    merged = offense_probs.merge(
        defense_probs,
        on=["season", "team", "player_id"],
        how="inner",
        suffixes=("_offense", "_defense"),
    )
    if merged.empty:
        return pd.DataFrame()

    rows = []
    for _, row in merged.iterrows():
        offense_map = row.get("offense_probabilities", {}) or {}
        defense_map = row.get("defense_probabilities", {}) or {}
        joint: dict[str, float] = {}
        for offense_token, offense_weight in offense_map.items():
            for defense_token, defense_weight in defense_map.items():
                joint[f"{offense_token} | {defense_token}"] = float(offense_weight) * float(defense_weight)
        if not joint:
            continue
        rows.append(
            {
                "season": row["season"],
                "team": row["team"],
                "player_id": row["player_id"],
                "player_name": row.get("player_name_offense", row.get("player_name_defense", "")),
                "probabilities": joint,
            }
        )
    return pd.DataFrame(rows)


def _build_team_features_from_probability_frame(
    frame: pd.DataFrame,
    *,
    mode: str,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()

    rows = []
    for (season, team), group in frame.groupby(["season", "team"], sort=False):
        token_weights: dict[str, float] = {}
        for _, row in group.iterrows():
            probs = row.get("probabilities") or {}
            for token, weight in probs.items():
                token_weights[token] = token_weights.get(token, 0.0) + float(weight)

        total_weight = sum(token_weights.values())
        if total_weight > 0:
            token_weights = {token: weight / total_weight for token, weight in token_weights.items()}

        feature_row: dict[str, float] = {}
        ordered_tokens = sorted(token_weights)
        if mode in {"presence", "hybrid"}:
            for token, weight in token_weights.items():
                feature_row[f"token={token}"] = weight
        if mode in {"pair", "hybrid"}:
            for left, right in combinations(ordered_tokens, 2):
                feature_row[f"pair={left} + {right}"] = token_weights[left] * token_weights[right]

        rows.append({"season": season, "team": team, "feature_row": feature_row})

    return pd.DataFrame(rows)


def _confidence_from_silhouette(value: object) -> float:
    try:
        if pd.isna(value):
            return 0.0
        silhouette = float(value)
    except (TypeError, ValueError):
        return 0.0
    # Map silhouette to a bounded weight where better separation carries more weight.
    return max(0.0, min(1.0, 1.0 / (1.0 + math.exp(-4.0 * silhouette))))


def _weight_from_row(row: pd.Series, *, source: str) -> float:
    if source == "offense":
        return max(0.0, _safe_float(row.get("archetype_cluster_confidence"), 0.0))
    if source == "defense":
        return _confidence_from_silhouette(row.get("defense_silhouette"))
    if source == "combined":
        offense_conf = max(0.0, _safe_float(row.get("archetype_cluster_confidence"), 0.0))
        defense_conf = _confidence_from_silhouette(row.get("defense_silhouette"))
        return offense_conf * defense_conf
    raise ValueError(f"Unknown soft-assignment source: {source}")


def _build_weighted_team_features(
    frame: pd.DataFrame,
    *,
    token_col: str,
    source: str,
    mode: str,
) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()

    rows = []
    for (season, team), group in frame.groupby(["season", "team"], sort=False):
        token_weights: dict[str, float] = {}
        for _, row in group.iterrows():
            token = _single_token(row.get(token_col))
            if token is None:
                continue
            weight = _weight_from_row(row, source=source)
            if weight <= 0:
                continue
            token_weights[token] = token_weights.get(token, 0.0) + weight

        total_weight = sum(token_weights.values())
        if total_weight > 0:
            token_weights = {token: weight / total_weight for token, weight in token_weights.items()}

        feature_row: dict[str, float] = {}
        ordered_tokens = sorted(token_weights)
        if mode in {"presence", "hybrid"}:
            for token, weight in token_weights.items():
                feature_row[f"token={token}"] = weight
        if mode in {"pair", "hybrid"}:
            for left, right in combinations(ordered_tokens, 2):
                feature_row[f"pair={left} + {right}"] = token_weights[left] * token_weights[right]

        rows.append(
            {
                "season": season,
                "team": team,
                "feature_row": feature_row,
            }
        )

    return pd.DataFrame(rows)


def _iter_pairs(tokens: Iterable[str]) -> list[str]:
    ordered = sorted(set(tokens))
    return [f"{left} + {right}" for left, right in combinations(ordered, 2)]


def _load_token_lookup(
    frame: pd.DataFrame,
    *,
    set_col: str,
    outcome_col: str = "made_conf_finals",
    alpha: float = DEFAULT_ALPHA,
) -> dict[str, object]:
    if frame.empty:
        return {"global_rate": 0.0, "lookup": {}, "counts": {}}

    global_rate = float(frame[outcome_col].mean())
    counts: dict[str, int] = {}
    hits: dict[str, float] = {}
    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
            hits[token] = hits.get(token, 0.0) + float(bool(row.get(outcome_col, False)))

    lookup: dict[str, float] = {}
    for token, count in counts.items():
        raw_rate = hits[token] / count
        lookup[token] = (hits[token] + alpha * global_rate) / (count + alpha)

    return {"global_rate": global_rate, "lookup": lookup, "counts": counts}


def _load_pair_lookup(
    frame: pd.DataFrame,
    *,
    set_col: str,
    outcome_col: str = "made_conf_finals",
    alpha: float = DEFAULT_ALPHA,
) -> dict[str, object]:
    if frame.empty:
        return {"global_rate": 0.0, "lookup": {}, "counts": {}}

    global_rate = float(frame[outcome_col].mean())
    counts: dict[str, int] = {}
    hits: dict[str, float] = {}
    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        for pair in _iter_pairs(tokens):
            counts[pair] = counts.get(pair, 0) + 1
            hits[pair] = hits.get(pair, 0.0) + float(bool(row.get(outcome_col, False)))

    lookup: dict[str, float] = {}
    for pair, count in counts.items():
        lookup[pair] = (hits[pair] + alpha * global_rate) / (count + alpha)

    return {"global_rate": global_rate, "lookup": lookup, "counts": counts}


def _load_pair_stat_lookup(
    frame: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    if frame.empty:
        return {}

    lookup: dict[str, dict[str, float]] = {}
    for _, row in frame.iterrows():
        pair = str(row.get("archetype_pair", "")).strip()
        if not pair or pair == "UNKNOWN":
            continue
        lookup[pair] = {
            "team_seasons": _safe_float(row.get("team_seasons"), 0.0),
            "playoff_rate": _safe_float(row.get("playoff_rate"), 0.0),
            "avg_series_wins": _safe_float(row.get("avg_series_wins"), 0.0),
            "conf_finals_rate": _safe_float(row.get("conf_finals_rate"), 0.0),
            "finals_rate": _safe_float(row.get("finals_rate"), 0.0),
            "championship_rate": _safe_float(row.get("championship_rate"), 0.0),
            "championships": _safe_float(row.get("championships"), 0.0),
            "conf_finals": _safe_float(row.get("conf_finals"), 0.0),
            "finals": _safe_float(row.get("finals"), 0.0),
        }
    return lookup


def _score_frame(
    frame: pd.DataFrame,
    *,
    set_col: str,
    token_lookup: dict[str, object],
    pair_lookup: dict[str, object],
    pair_mode: bool,
) -> pd.DataFrame:
    rows = []
    token_map = token_lookup["lookup"]
    pair_map = pair_lookup["lookup"]
    token_base = float(token_lookup["global_rate"])
    pair_base = float(pair_lookup["global_rate"])

    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        if pair_mode:
            keys = _iter_pairs(tokens)
            lookup = pair_map
            default = pair_base
        else:
            keys = tokens
            lookup = token_map
            default = token_base

        if keys:
            matched = [float(lookup.get(key, default)) for key in keys]
            score = sum(matched) / len(matched)
            coverage = sum(1 for key in keys if key in lookup) / len(keys)
        else:
            score = default
            coverage = 0.0

        rows.append(
            {
                "season": row["season"],
                "team": row["team"],
                "score": score,
                "coverage": coverage,
            }
        )

    return pd.DataFrame(rows)


def _build_pair_summary_feature_frame(
    frame: pd.DataFrame,
    *,
    set_col: str,
    pair_lookup: dict[str, dict[str, float]],
) -> pd.DataFrame:
    if frame.empty or not pair_lookup:
        return pd.DataFrame()

    rows = []
    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        pairs = _iter_pairs(tokens)
        stats = [pair_lookup[pair] for pair in pairs if pair in pair_lookup]
        if not stats:
            continue

        def _mean(key: str) -> float:
            values = [float(item[key]) for item in stats]
            return float(sum(values) / len(values)) if values else 0.0

        def _sum(key: str) -> float:
            return float(sum(float(item[key]) for item in stats))

        feature_row = {
            "pair_count": float(len(pairs)),
            "pair_hit_rate": float(len(stats) / len(pairs)) if pairs else 0.0,
            "pair_team_seasons_mean": _mean("team_seasons"),
            "pair_avg_series_wins_mean": _mean("avg_series_wins"),
            "pair_conf_finals_rate_mean": _mean("conf_finals_rate"),
            "pair_finals_rate_mean": _mean("finals_rate"),
            "pair_championship_rate_mean": _mean("championship_rate"),
            "pair_conf_finals_sum": _sum("conf_finals"),
            "pair_finals_sum": _sum("finals"),
            "pair_championship_sum": _sum("championships"),
            "pair_team_seasons_sum": _sum("team_seasons"),
            "pair_cf_rate_sum": _sum("conf_finals_rate"),
            "pair_finals_rate_sum": _sum("finals_rate"),
            "pair_title_rate_sum": _sum("championship_rate"),
            "pair_best_series_wins": max(float(item["avg_series_wins"]) for item in stats),
            "pair_best_cf_rate": max(float(item["conf_finals_rate"]) for item in stats),
            "pair_best_title_rate": max(float(item["championship_rate"]) for item in stats),
        }

        rows.append(
            {
                "season": row["season"],
                "team": row["team"],
                "feature_row": feature_row,
            }
        )

    return pd.DataFrame(rows)


def _build_pair_score_summary_feature_frame(
    frame: pd.DataFrame,
    *,
    set_col: str,
    pair_lookup: dict[str, object],
    default_score: float,
) -> pd.DataFrame:
    if frame.empty or not pair_lookup:
        return pd.DataFrame()

    lookup = pair_lookup["lookup"]
    global_rate = float(pair_lookup["global_rate"])
    baseline = float(default_score if default_score is not None else global_rate)

    rows = []
    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        pairs = _iter_pairs(tokens)
        if not pairs:
            continue
        scores = [float(lookup.get(pair, baseline)) for pair in pairs]
        score_series = pd.Series(scores, dtype=float)
        top_k = min(3, len(scores))
        top_scores = sorted(scores, reverse=True)[:top_k]
        feature_row = {
            "pair_count": float(len(pairs)),
            "pair_score_mean": float(score_series.mean()),
            "pair_score_std": float(score_series.std(ddof=0)) if len(scores) > 1 else 0.0,
            "pair_score_min": float(score_series.min()),
            "pair_score_max": float(score_series.max()),
            "pair_score_median": float(score_series.median()),
            "pair_score_top3_mean": float(sum(top_scores) / len(top_scores)) if top_scores else baseline,
            "pair_score_above_global_share": float(sum(score > global_rate for score in scores) / len(scores)),
            "pair_score_sum": float(score_series.sum()),
        }
        rows.append(
            {
                "season": row["season"],
                "team": row["team"],
                "feature_row": feature_row,
            }
        )

    return pd.DataFrame(rows)


def _oof_pair_summary_scores(
    frame: pd.DataFrame,
    *,
    set_col: str,
    era_col: str,
    era_bounds: list[tuple[str, int, int]],
    outcome_col: str = "made_conf_finals",
    c_value: float = 0.3,
) -> pd.DataFrame:
    scored_frames = []
    available_eras = [label for label, _, _ in era_bounds if label in set(frame[era_col].dropna().unique())]
    if not available_eras:
        return pd.DataFrame()

    frame = frame.reset_index(drop=True).copy()

    for era in available_eras:
        train_mask = frame[era_col] != era
        test_mask = frame[era_col] == era
        train = frame.loc[train_mask].copy()
        test = frame.loc[test_mask].copy()
        if train.empty or test.empty:
            continue

        pair_lookup = _load_pair_lookup(train, set_col=set_col, outcome_col=outcome_col, alpha=DEFAULT_ALPHA)
        train_features = _build_pair_score_summary_feature_frame(
            train,
            set_col=set_col,
            pair_lookup=pair_lookup,
            default_score=float(pair_lookup["global_rate"]),
        )
        test_features = _build_pair_score_summary_feature_frame(
            test,
            set_col=set_col,
            pair_lookup=pair_lookup,
            default_score=float(pair_lookup["global_rate"]),
        )
        if train_features.empty or test_features.empty:
            continue

        train_merged = train[["season", "team", era_col, outcome_col]].merge(train_features, on=["season", "team"], how="inner")
        test_merged = test[["season", "team", era_col, outcome_col]].merge(test_features, on=["season", "team"], how="inner")
        if train_merged.empty or test_merged.empty:
            continue

        train_dicts = train_merged["feature_row"].tolist()
        test_dicts = test_merged["feature_row"].tolist()
        vectorizer = DictVectorizer(sparse=True)
        X_train = vectorizer.fit_transform(train_dicts)
        X_test = vectorizer.transform(test_dicts)
        y_train = train_merged[outcome_col].astype(int)

        if y_train.nunique() < 2:
            scores = [float(y_train.mean())] * len(test_merged)
        else:
            model = LogisticRegression(
                C=c_value,
                class_weight="balanced",
                max_iter=4000,
                solver="liblinear",
            )
            model.fit(X_train, y_train)
            scores = model.predict_proba(X_test)[:, 1]

        vocab = set(vectorizer.vocabulary_.keys())
        coverage = []
        for features in test_dicts:
            keys = list(features.keys())
            if not keys:
                coverage.append(0.0)
            else:
                matched = sum(1 for key in keys if key in vocab)
                coverage.append(matched / len(keys))

        scored = pd.DataFrame(
            {
                "season": test_merged["season"].values,
                "team": test_merged["team"].values,
                "score": scores,
                "coverage": coverage,
                "era": era,
            }
        )
        scored_frames.append(scored)

    if not scored_frames:
        return pd.DataFrame()
    return pd.concat(scored_frames, ignore_index=True)


def _roc_auc(y_true: pd.Series, y_score: pd.Series) -> float:
    frame = pd.DataFrame({"y": y_true.astype(int), "score": y_score.astype(float)}).dropna()
    positives = frame[frame["y"] == 1]
    negatives = frame[frame["y"] == 0]
    n_pos = len(positives)
    n_neg = len(negatives)
    if n_pos == 0 or n_neg == 0:
        return float("nan")
    ranks = frame["score"].rank(method="average")
    sum_pos = float(ranks[frame["y"] == 1].sum())
    auc = (sum_pos - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg)
    return float(auc)


def _top_decile_rate(frame: pd.DataFrame, score_col: str, outcome_col: str) -> tuple[float, float]:
    clean = frame[[score_col, outcome_col]].dropna().copy()
    if clean.empty:
        return float("nan"), float("nan")
    n_top = max(1, math.ceil(len(clean) * 0.10))
    top = clean.sort_values(score_col, ascending=False).head(n_top)
    top_rate = float(top[outcome_col].mean())
    base_rate = float(clean[outcome_col].mean())
    lift = top_rate / base_rate if base_rate else float("nan")
    return top_rate, lift


def _summarize_predictions(
    frame: pd.DataFrame,
    *,
    score_col: str,
    outcome_cols: list[str],
) -> dict[str, object]:
    summary = {
        "rows": int(len(frame)),
        "score_mean": float(frame[score_col].mean()) if not frame.empty else float("nan"),
        "score_std": float(frame[score_col].std()) if not frame.empty else float("nan"),
        "coverage_mean": float(frame["coverage"].mean()) if "coverage" in frame.columns and not frame.empty else float("nan"),
    }
    for outcome_col in outcome_cols:
        auc = _roc_auc(frame[outcome_col], frame[score_col])
        top_rate, lift = _top_decile_rate(frame, score_col, outcome_col)
        summary[f"{outcome_col}_auc"] = auc
        summary[f"{outcome_col}_top_decile_rate"] = top_rate
        summary[f"{outcome_col}_top_decile_lift"] = lift
        summary[f"{outcome_col}_base_rate"] = float(frame[outcome_col].mean()) if not frame.empty else float("nan")
    return summary


def _out_of_fold_scores(
    frame: pd.DataFrame,
    *,
    set_col: str,
    era_col: str,
    era_bounds: list[tuple[str, int, int]],
    pair_mode: bool,
    outcome_col: str = "made_conf_finals",
    alpha: float = DEFAULT_ALPHA,
) -> pd.DataFrame:
    scored_frames = []
    available_eras = [label for label, _, _ in era_bounds if label in set(frame[era_col].dropna().unique())]
    for era in available_eras:
        train = frame[frame[era_col] != era].copy()
        test = frame[frame[era_col] == era].copy()
        if train.empty or test.empty:
            continue
        token_lookup = _load_token_lookup(train, set_col=set_col, outcome_col=outcome_col, alpha=alpha)
        pair_lookup = _load_pair_lookup(train, set_col=set_col, outcome_col=outcome_col, alpha=alpha)
        scored = _score_frame(test, set_col=set_col, token_lookup=token_lookup, pair_lookup=pair_lookup, pair_mode=pair_mode)
        scored["era"] = era
        scored_frames.append(scored)

    if not scored_frames:
        return pd.DataFrame()
    return pd.concat(scored_frames, ignore_index=True)


def _format_pct(value: float) -> str:
    if value is None or pd.isna(value):
        return "NA"
    return f"{value * 100:.1f}%"


def _add_era_percentile_score(frame: pd.DataFrame, *, score_col: str, era_col: str, new_col: str) -> pd.DataFrame:
    if frame.empty or score_col not in frame.columns or era_col not in frame.columns:
        return frame.copy()

    result = frame.copy()
    result[new_col] = result.groupby(era_col)[score_col].rank(pct=True, method="average")
    return result


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in frame.iterrows():
        cells = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                cells.append(f"{value:.4f}")
            else:
                cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _feature_dicts(frame: pd.DataFrame, *, set_col: str, mode: str) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for _, row in frame.iterrows():
        tokens = _normalize_token_list(row.get(set_col, ""))
        feature_row: dict[str, float] = {}
        if mode in {"presence", "hybrid"}:
            for token in tokens:
                feature_row[f"token={token}"] = 1.0
        if mode in {"pair", "hybrid"}:
            for pair in _iter_pairs(tokens):
                feature_row[f"pair={pair}"] = 1.0
        rows.append(feature_row)
    return rows


def _oof_logistic_scores(
    frame: pd.DataFrame,
    *,
    set_col: str,
    era_col: str,
    era_bounds: list[tuple[str, int, int]],
    mode: str,
    outcome_col: str = "made_conf_finals",
    c_value: float = 0.3,
) -> pd.DataFrame:
    scored_frames = []
    available_eras = [label for label, _, _ in era_bounds if label in set(frame[era_col].dropna().unique())]
    if not available_eras:
        return pd.DataFrame()

    feature_rows = _feature_dicts(frame, set_col=set_col, mode=mode)
    frame = frame.reset_index(drop=True).copy()
    feature_frame = pd.DataFrame({"feature_row": feature_rows})

    for era in available_eras:
        train_mask = frame[era_col] != era
        test_mask = frame[era_col] == era
        train = frame.loc[train_mask].copy()
        test = frame.loc[test_mask].copy()
        if train.empty or test.empty:
            continue

        train_features = [feature_rows[idx] for idx in frame.index[train_mask]]
        test_features = [feature_rows[idx] for idx in frame.index[test_mask]]
        vectorizer = DictVectorizer(sparse=True)
        X_train = vectorizer.fit_transform(train_features)
        X_test = vectorizer.transform(test_features)
        y_train = train[outcome_col].astype(int)

        if y_train.nunique() < 2:
            constant = float(y_train.mean())
            scores = [constant] * len(test)
        else:
            model = LogisticRegression(
                C=c_value,
                class_weight="balanced",
                max_iter=4000,
                solver="liblinear",
            )
            model.fit(X_train, y_train)
            scores = model.predict_proba(X_test)[:, 1]

        vocab = set(vectorizer.vocabulary_.keys())
        coverage = []
        for features in test_features:
            keys = list(features.keys())
            if not keys:
                coverage.append(0.0)
            else:
                matched = sum(1 for key in keys if key in vocab)
                coverage.append(matched / len(keys))

        scored = pd.DataFrame(
            {
                "season": test["season"].values,
                "team": test["team"].values,
                "score": scores,
                "coverage": coverage,
                "era": era,
            }
        )
        scored_frames.append(scored)

    if not scored_frames:
        return pd.DataFrame()
    return pd.concat(scored_frames, ignore_index=True)


def _oof_logistic_scores_from_features(
    frame: pd.DataFrame,
    *,
    feature_col: str,
    era_col: str,
    era_bounds: list[tuple[str, int, int]],
    outcome_col: str = "made_conf_finals",
    c_value: float = 0.3,
) -> pd.DataFrame:
    scored_frames = []
    available_eras = [label for label, _, _ in era_bounds if label in set(frame[era_col].dropna().unique())]
    if not available_eras:
        return pd.DataFrame()

    frame = frame.reset_index(drop=True).copy()

    for era in available_eras:
        train_mask = frame[era_col] != era
        test_mask = frame[era_col] == era
        train = frame.loc[train_mask].copy()
        test = frame.loc[test_mask].copy()
        if train.empty or test.empty:
            continue

        train_features = train[feature_col].tolist()
        test_features = test[feature_col].tolist()
        vectorizer = DictVectorizer(sparse=True)
        X_train = vectorizer.fit_transform(train_features)
        X_test = vectorizer.transform(test_features)
        y_train = train[outcome_col].astype(int)

        if y_train.nunique() < 2:
            constant = float(y_train.mean())
            scores = [constant] * len(test)
        else:
            model = LogisticRegression(
                C=c_value,
                class_weight="balanced",
                max_iter=4000,
                solver="liblinear",
            )
            model.fit(X_train, y_train)
            scores = model.predict_proba(X_test)[:, 1]

        vocab = set(vectorizer.vocabulary_.keys())
        coverage = []
        for features in test_features:
            keys = list(features.keys())
            if not keys:
                coverage.append(0.0)
            else:
                matched = sum(1 for key in keys if key in vocab)
                coverage.append(matched / len(keys))

        scored = pd.DataFrame(
            {
                "season": test["season"].values,
                "team": test["team"].values,
                "score": scores,
                "coverage": coverage,
                "era": era,
            }
        )
        scored_frames.append(scored)

    if not scored_frames:
        return pd.DataFrame()
    return pd.concat(scored_frames, ignore_index=True)


def _build_model_table(
    frame: pd.DataFrame,
    *,
    label: str,
    set_col: str,
    era_bounds: list[tuple[str, int, int]],
    pair_mode: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work = _attach_targets(work)
    work["era"] = work["season"].map(lambda season: _assign_era(str(season), era_bounds))
    work = work[work["era"].notna()].copy()
    work = work[work[set_col].notna()].copy()
    work = work[work[set_col].astype(str).str.contains("UNKNOWN") == False].copy()

    scored = _out_of_fold_scores(
        work,
        set_col=set_col,
        era_col="era",
        era_bounds=era_bounds,
        pair_mode=pair_mode,
    )
    merged = work.merge(scored, on=["season", "team"], how="inner", suffixes=("", "_pred"))
    merged = merged.rename(columns={"score": f"{label}_score", "coverage": f"{label}_coverage"})

    summary = _summarize_predictions(
        merged.rename(columns={f"{label}_score": "score", f"{label}_coverage": "coverage"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(merged)),
            "window": f"{_season_start(str(merged['season'].min()))}-{_season_start(str(merged['season'].max()))}",
            "era_count": int(merged["era"].nunique()),
            "coverage_mean": float(merged[f"{label}_coverage"].mean()) if not merged.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), merged


def _build_logistic_model_table(
    frame: pd.DataFrame,
    *,
    label: str,
    set_col: str,
    era_bounds: list[tuple[str, int, int]],
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work = _attach_targets(work)
    work["era"] = work["season"].map(lambda season: _assign_era(str(season), era_bounds))
    work = work[work["era"].notna()].copy()
    work = work[work[set_col].notna()].copy()
    work = work[work[set_col].astype(str).str.contains("UNKNOWN") == False].copy()

    scored = _oof_logistic_scores(
        work,
        set_col=set_col,
        era_col="era",
        era_bounds=era_bounds,
        mode=mode,
    )
    merged = work.merge(scored, on=["season", "team", "era"], how="inner", suffixes=("", "_pred"))
    merged = merged.rename(columns={"score": f"{label}_score", "coverage": f"{label}_coverage"})

    summary = _summarize_predictions(
        merged.rename(columns={f"{label}_score": "score", f"{label}_coverage": "coverage"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(merged)),
            "window": f"{_season_start(str(merged['season'].min()))}-{_season_start(str(merged['season'].max()))}",
            "era_count": int(merged["era"].nunique()),
            "coverage_mean": float(merged[f"{label}_coverage"].mean()) if not merged.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), merged


def _build_soft_logistic_model_table(
    frame: pd.DataFrame,
    *,
    label: str,
    token_col: str,
    source: str,
    era_bounds: list[tuple[str, int, int]],
    mode: str,
    outcome_frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work = _attach_targets(work)
    work["era"] = work["season"].map(lambda season: _assign_era(str(season), era_bounds))
    work = work[work["era"].notna()].copy()
    work = work[work[token_col].notna()].copy()
    work = work[work[token_col].astype(str).str.contains("UNKNOWN") == False].copy()

    team_features = _build_weighted_team_features(
        work,
        token_col=token_col,
        source=source,
        mode=mode,
    )
    if team_features.empty:
        return pd.DataFrame(), pd.DataFrame()

    target_cols = [
        "season",
        "team",
        PRIMARY_OUTCOME,
        "made_finals",
        "won_championship",
    ]
    targets = outcome_frame.copy()
    targets = _attach_targets(targets)
    targets["era"] = targets["season"].map(lambda season: _assign_era(str(season), era_bounds))
    targets = targets[targets["era"].notna()].copy()
    targets = targets[target_cols + ["era"]].drop_duplicates(subset=["season", "team"]).copy()
    merged_work = targets.merge(team_features, on=["season", "team"], how="inner")

    scored = _oof_logistic_scores_from_features(
        merged_work,
        feature_col="feature_row",
        era_col="era",
        era_bounds=era_bounds,
    )
    merged = merged_work.merge(scored, on=["season", "team", "era"], how="inner", suffixes=("", "_pred"))
    merged = merged.rename(columns={"score": f"{label}_score", "coverage": f"{label}_coverage"})

    summary = _summarize_predictions(
        merged.rename(columns={f"{label}_score": "score", f"{label}_coverage": "coverage"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(merged)),
            "window": f"{_season_start(str(merged['season'].min()))}-{_season_start(str(merged['season'].max()))}",
            "era_count": int(merged["era"].nunique()),
            "coverage_mean": float(merged[f"{label}_coverage"].mean()) if not merged.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), merged


def _build_soft_probability_model_table(
    probability_frame: pd.DataFrame,
    outcome_frame: pd.DataFrame,
    *,
    label: str,
    era_bounds: list[tuple[str, int, int]],
    mode: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if probability_frame.empty or outcome_frame.empty:
        return pd.DataFrame(), pd.DataFrame()

    targets = outcome_frame.copy()
    targets = _attach_targets(targets)
    targets["era"] = targets["season"].map(lambda season: _assign_era(str(season), era_bounds))
    targets = targets[targets["era"].notna()].copy()
    targets = targets[[
        "season",
        "team",
        "era",
        PRIMARY_OUTCOME,
        "made_finals",
        "won_championship",
    ]].drop_duplicates(subset=["season", "team"]).copy()

    team_features = _build_team_features_from_probability_frame(
        probability_frame,
        mode=mode,
    )
    if team_features.empty:
        return pd.DataFrame(), pd.DataFrame()

    merged_work = targets.merge(team_features, on=["season", "team"], how="inner")
    if merged_work.empty:
        return pd.DataFrame(), pd.DataFrame()

    scored = _oof_logistic_scores_from_features(
        merged_work,
        feature_col="feature_row",
        era_col="era",
        era_bounds=era_bounds,
    )
    merged = merged_work.merge(scored, on=["season", "team", "era"], how="inner", suffixes=("", "_pred"))
    merged = merged.rename(columns={"score": f"{label}_score", "coverage": f"{label}_coverage"})

    summary = _summarize_predictions(
        merged.rename(columns={f"{label}_score": "score", f"{label}_coverage": "coverage"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(merged)),
            "window": f"{_season_start(str(merged['season'].min()))}-{_season_start(str(merged['season'].max()))}",
            "era_count": int(merged["era"].nunique()),
            "coverage_mean": float(merged[f"{label}_coverage"].mean()) if not merged.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), merged


def _build_pair_summary_model_table(
    frame: pd.DataFrame,
    *,
    label: str,
    set_col: str,
    era_bounds: list[tuple[str, int, int]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = frame.copy()
    work = _attach_targets(work)
    work["era"] = work["season"].map(lambda season: _assign_era(str(season), era_bounds))
    work = work[work["era"].notna()].copy()
    work = work[work[set_col].notna()].copy()
    work = work[work[set_col].astype(str).str.contains("UNKNOWN") == False].copy()

    scored = _oof_pair_summary_scores(
        work,
        set_col=set_col,
        era_col="era",
        era_bounds=era_bounds,
    )
    merged = work.merge(scored, on=["season", "team", "era"], how="inner", suffixes=("", "_pred"))
    merged = merged.rename(columns={"score": f"{label}_score", "coverage": f"{label}_coverage"})

    summary = _summarize_predictions(
        merged.rename(columns={f"{label}_score": "score", f"{label}_coverage": "coverage"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(merged)),
            "window": f"{_season_start(str(merged['season'].min()))}-{_season_start(str(merged['season'].max()))}",
            "era_count": int(merged["era"].nunique()),
            "coverage_mean": float(merged[f"{label}_coverage"].mean()) if not merged.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), merged


def _build_standardized_centroid_combo_table(
    first_frame: pd.DataFrame,
    second_frame: pd.DataFrame,
    *,
    label: str,
    era_bounds: list[tuple[str, int, int]],
    first_score_col: str,
    second_score_col: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if first_frame.empty or second_frame.empty:
        return pd.DataFrame(), pd.DataFrame()

    target_cols = [
        "season",
        "team",
        "era",
        PRIMARY_OUTCOME,
        "made_finals",
        "won_championship",
    ]

    first_cols = target_cols + [first_score_col, f"{first_score_col.replace('_score', '')}_coverage"]
    second_cols = target_cols + [second_score_col, f"{second_score_col.replace('_score', '')}_coverage"]

    first_work = first_frame[first_cols].drop_duplicates(subset=["season", "team", "era"]).copy()
    second_work = second_frame[second_cols].drop_duplicates(subset=["season", "team", "era"]).copy()
    first_work = first_work.rename(
        columns={
            first_score_col: "first_score",
            f"{first_score_col.replace('_score', '')}_coverage": "first_coverage",
        }
    )
    second_work = second_work.rename(
        columns={
            second_score_col: "second_score",
            f"{second_score_col.replace('_score', '')}_coverage": "second_coverage",
        }
    )

    merged = first_work.merge(
        second_work,
        on=target_cols,
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    available_eras = [label for label, _, _ in era_bounds if label in set(merged["era"].dropna().unique())]
    scored_rows = []
    feature_cols = ["first_score", "second_score"]

    for era in available_eras:
        era_frame = merged[merged["era"] == era].copy()
        seasons = sorted(era_frame["season"].dropna().unique())
        for holdout_season in seasons:
            train = era_frame[era_frame["season"] != holdout_season].copy()
            test = era_frame[era_frame["season"] == holdout_season].copy()
            if train.empty or test.empty:
                continue

            train_scores = train[feature_cols].astype(float)
            test_scores = test[feature_cols].astype(float)
            train_mean = train_scores.mean()
            train_std = train_scores.std(ddof=0).replace(0.0, 1.0)
            train_z = (train_scores - train_mean) / train_std
            test_z = (test_scores - train_mean) / train_std

            positive = train[train[PRIMARY_OUTCOME].astype(bool)].copy()
            if positive.empty:
                positive_centroid = train_z.mean()
            else:
                positive_centroid = train_z.loc[positive.index].mean()

            deltas = test_z - positive_centroid
            scores = -np.sqrt((deltas ** 2).sum(axis=1))
            coverage = (
                test["first_coverage"].astype(float).fillna(0.0).values
                + test["second_coverage"].astype(float).fillna(0.0).values
            ) / 2.0

            scored_rows.append(
                pd.DataFrame(
                    {
                        "season": test["season"].values,
                        "team": test["team"].values,
                        "score": scores.values,
                        "coverage": coverage,
                        "era": era,
                    }
                )
            )

    if not scored_rows:
        return pd.DataFrame(), pd.DataFrame()

    scored = pd.concat(scored_rows, ignore_index=True)
    summary = _summarize_predictions(
        scored.merge(
            merged[target_cols].drop_duplicates(subset=["season", "team", "era"]),
            on=["season", "team", "era"],
            how="left",
        ),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(scored)),
            "window": f"{_season_start(str(scored['season'].min()))}-{_season_start(str(scored['season'].max()))}",
            "era_count": int(scored["era"].nunique()),
            "coverage_mean": float(scored["coverage"].mean()) if not scored.empty else float("nan"),
        }
    )
    return pd.DataFrame([summary]), scored


def _build_standardized_blend_sweep_table(
    first_frame: pd.DataFrame,
    second_frame: pd.DataFrame,
    *,
    label: str,
    era_bounds: list[tuple[str, int, int]],
    first_score_col: str,
    second_score_col: str,
    alpha_grid: list[float],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if first_frame.empty or second_frame.empty:
        return pd.DataFrame(), pd.DataFrame()

    target_cols = [
        "season",
        "team",
        "era",
        PRIMARY_OUTCOME,
        "made_finals",
        "won_championship",
    ]

    first_coverage_col = f"{first_score_col.replace('_score', '')}_coverage"
    second_coverage_col = f"{second_score_col.replace('_score', '')}_coverage"
    first_work = first_frame[target_cols + [first_score_col, first_coverage_col]].drop_duplicates(subset=["season", "team", "era"]).copy()
    second_work = second_frame[target_cols + [second_score_col, second_coverage_col]].drop_duplicates(subset=["season", "team", "era"]).copy()
    first_work = first_work.rename(columns={first_score_col: "first_score", first_coverage_col: "first_coverage"})
    second_work = second_work.rename(columns={second_score_col: "second_score", second_coverage_col: "second_coverage"})

    merged = first_work.merge(second_work, on=target_cols, how="inner")
    if merged.empty:
        return pd.DataFrame(), pd.DataFrame()

    available_eras = [label for label, _, _ in era_bounds if label in set(merged["era"].dropna().unique())]
    scored_rows = []

    for era in available_eras:
        era_frame = merged[merged["era"] == era].copy()
        if era_frame.empty:
            continue
        train = merged[merged["era"] != era].copy()
        if train.empty:
            continue

        train_scores = train[["first_score", "second_score"]].astype(float)
        test_scores = era_frame[["first_score", "second_score"]].astype(float)
        train_mean = train_scores.mean()
        train_std = train_scores.std(ddof=0).replace(0.0, 1.0)
        train_z = (train_scores - train_mean) / train_std
        test_z = (test_scores - train_mean) / train_std

        for alpha in alpha_grid:
            beta = 1.0 - float(alpha)
            scores = alpha * test_z["first_score"] + beta * test_z["second_score"]
            scored_rows.append(
                pd.DataFrame(
                    {
                        "season": era_frame["season"].values,
                        "team": era_frame["team"].values,
                        "alpha": float(alpha),
                        "score": scores.values,
                        "coverage": (
                            era_frame["first_coverage"].astype(float).fillna(0.0).values
                            + era_frame["second_coverage"].astype(float).fillna(0.0).values
                        ) / 2.0,
                        "era": era,
                        PRIMARY_OUTCOME: era_frame[PRIMARY_OUTCOME].values,
                        "made_conf_finals": era_frame["made_conf_finals"].values,
                        "made_finals": era_frame["made_finals"].values,
                        "won_championship": era_frame["won_championship"].values,
                    }
                )
            )

    if not scored_rows:
        return pd.DataFrame(), pd.DataFrame()

    scored = pd.concat(scored_rows, ignore_index=True)
    summary_rows = []
    for alpha, alpha_frame in scored.groupby("alpha", sort=True):
        summary = _summarize_predictions(
            alpha_frame,
            score_col="score",
            outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
        )
        summary.update(
            {
                "label": f"{label}_a{float(alpha):.2f}",
                "sweep_label": label,
                "alpha": float(alpha),
                "rows": int(len(alpha_frame)),
                "window": f"{_season_start(str(alpha_frame['season'].min()))}-{_season_start(str(alpha_frame['season'].max()))}",
                "era_count": int(alpha_frame["era"].nunique()),
                "coverage_mean": float(alpha_frame["coverage"].mean()) if not alpha_frame.empty else float("nan"),
            }
        )
        summary_rows.append(summary)

    summary_df = pd.DataFrame(summary_rows)
    return summary_df, scored


def _temperature_sweep_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No sweep rows._"
    cols = ["temperature", "label", f"{PRIMARY_OUTCOME}_auc", "made_finals_auc", "coverage_mean"]
    display = frame[cols].copy()
    display["temperature"] = display["temperature"].map(lambda v: f"{v:.2f}")
    display[f"{PRIMARY_OUTCOME}_auc"] = display[f"{PRIMARY_OUTCOME}_auc"].map(_format_pct)
    display["made_finals_auc"] = display["made_finals_auc"].map(_format_pct)
    display["coverage_mean"] = display["coverage_mean"].map(lambda v: f"{v:.2f}" if not pd.isna(v) else "NA")
    return _markdown_table(display, cols)


def _baseline_summary(frame: pd.DataFrame, *, label: str, score_col: str) -> pd.DataFrame:
    rows = frame.copy()
    rows = _attach_targets(rows)
    summary = _summarize_predictions(
        rows.rename(columns={score_col: "score"}),
        score_col="score",
        outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
    )
    summary.update(
        {
            "label": label,
            "rows": int(len(rows)),
            "window": f"{_season_start(str(rows['season'].min()))}-{_season_start(str(rows['season'].max()))}",
            "era_count": int(rows["era"].nunique()) if "era" in rows.columns else 0,
            "coverage_mean": float("nan"),
        }
    )
    return pd.DataFrame([summary])


def _render_summary_table(summary: pd.DataFrame) -> str:
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            [
                row["label"],
                row["window"],
                str(int(row["rows"])),
                str(int(row["era_count"])),
                _format_pct(row[f"{PRIMARY_OUTCOME}_auc"]),
                _format_pct(row["made_finals_auc"]),
                _format_pct(row["won_championship_auc"]),
                f"{row['coverage_mean']:.2f}" if not pd.isna(row["coverage_mean"]) else "NA",
            ]
        )
    return "\n".join(
        [
            "| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            *["| " + " | ".join(row) + " |" for row in rows],
        ]
    )


def _recent_fmvw_summary(modern_scores: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    fmvw = _read_csv(FMVW_TEAM_PATH)
    if fmvw.empty:
        return pd.DataFrame(), "_No FMVW backtest rows found._"
    if "season" not in fmvw.columns or "team" not in fmvw.columns:
        return pd.DataFrame(), "_FMVW backtest file is missing season/team columns._"

    modern_scores = _attach_targets(modern_scores)
    merged = modern_scores[["season", "team", PRIMARY_OUTCOME, "made_finals", "won_championship"]].merge(
        fmvw,
        on=["season", "team"],
        how="inner",
    )
    if merged.empty:
        return pd.DataFrame(), "_No overlap between modern scores and FMVW backtest rows._"

    rows = []
    for label, score_col in [
        ("FMVW predicted wins", "predicted_wins"),
        ("FMVW team FMV total", "team_fmv_total"),
    ]:
        if score_col not in merged.columns:
            continue
        summary = _summarize_predictions(
            merged.rename(columns={score_col: "score"}),
            score_col="score",
            outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
        )
        summary.update(
            {
                "label": label,
                "rows": int(len(merged)),
                "window": f"{merged['season'].min()} to {merged['season'].max()}",
                "era_count": int(merged["season"].nunique()),
                "coverage_mean": float("nan"),
            }
        )
        rows.append(summary)

    summary_df = pd.DataFrame(rows)
    if summary_df.empty:
        return summary_df, "_FMVW backtest file did not contain usable baseline columns._"
    return summary_df, ""


def _team_ops_summary() -> tuple[pd.DataFrame, str]:
    if not TEAM_OPS_COMPARISON_PATH.exists():
        return pd.DataFrame(), "_No team ops comparison summary found._"

    payload = json.loads(TEAM_OPS_COMPARISON_PATH.read_text(encoding="utf-8"))
    team_values = pd.DataFrame(payload.get("team_ops_backtest", {}).get("team_values", []))
    if team_values.empty:
        return pd.DataFrame(), "_Team ops comparison summary did not contain usable team rows._"

    playoff_source = _read_csv(OFFENSE_TEAM_PATH)[[
        "season",
        "team",
        "playoff_series_wins",
        "made_conf_finals",
        "made_finals",
        "won_championship",
    ]].drop_duplicates(subset=["season", "team"])

    merged = team_values.merge(playoff_source, on=["season", "team"], how="inner")
    if merged.empty:
        return pd.DataFrame(), "_No overlap between team ops rows and postseason outcomes._"

    merged = _attach_targets(merged)
    merged["season_start"] = merged["season"].astype(str).str.slice(0, 4).astype(int)
    rows = []
    for label, score_col, frame in [
        ("Team ops total score", "team_total_score", merged),
        ("Team ops total score (modern)", "team_total_score", merged[merged["season_start"] >= 2013].copy()),
        ("Team rate score", "team_rate_score", merged),
        ("Pressure score", "pressure_score", merged),
        ("Easy score", "easy_score", merged),
    ]:
        if frame.empty or score_col not in frame.columns:
            continue
        summary = _summarize_predictions(
            frame.rename(columns={score_col: "score"}),
            score_col="score",
            outcome_cols=[PRIMARY_OUTCOME, "made_conf_finals", "made_finals", "won_championship"],
        )
        summary.update(
            {
                "label": label,
                "rows": int(len(frame)),
                "window": f"{frame['season'].min()} to {frame['season'].max()}",
                "era_count": int(frame["season_start"].nunique()),
                "coverage_mean": float("nan"),
            }
        )
        rows.append(summary)

    summary_df = pd.DataFrame(rows)
    if summary_df.empty:
        return summary_df, "_Team ops comparison summary did not produce usable score rows._"
    return summary_df, ""


def _top_examples(frame: pd.DataFrame, score_col: str, label: str, n: int = 8) -> str:
    if frame.empty or score_col not in frame.columns:
        return "_No examples._"
    cols = ["season", "team", score_col, "made_conf_finals", "made_finals", "won_championship"]
    view = frame.sort_values(score_col, ascending=False).head(n)[cols].copy()
    view[score_col] = view[score_col].map(lambda v: f"{v:.4f}")
    view["made_conf_finals"] = view["made_conf_finals"].map(lambda v: "Y" if bool(v) else "N")
    view["made_finals"] = view["made_finals"].map(lambda v: "Y" if bool(v) else "N")
    view["won_championship"] = view["won_championship"].map(lambda v: "Y" if bool(v) else "N")
    return "\n".join(
        [
            f"### Top {n} {label} rows",
            "",
            _markdown_table(view, cols),
        ]
    )


def build_report(
    *,
    output_md: Path,
    output_json: Path,
) -> dict[str, object]:
    offense = _read_csv(OFFENSE_TEAM_PATH)
    offense_players = _read_csv(OFFENSE_PLAYER_PATH)
    defense = _read_csv(DEFENSE_TEAM_PATH)

    offense_era_bounds = [
        ("Era 1", 1995, 2006),
        ("Era 2", 2007, 2014),
        ("Era 3", 2015, 2025),
    ]
    modern_era_bounds = [
        ("Era 2", 2013, 2014),
        ("Era 3", 2015, 2025),
    ]

    offense_temperature_summaries = []
    offense_probability_frames: dict[float, pd.DataFrame] = {}
    for temperature in OFFENSE_SOFT_TEMPERATURE_SWEEP:
        temp_probabilities = _build_probability_frame(
            offense_players,
            cluster_summary_path=OFFENSE_CLUSTER_SUMMARY_PATH,
            feature_cols=OFFENSE_SOFT_FEATURES,
            position_col="archetype_position",
            probability_label="offense_probabilities",
            temperature=temperature,
        )
        if not temp_probabilities.empty:
            temp_probabilities = temp_probabilities.rename(columns={"offense_probabilities": "probabilities"})
        offense_probability_frames[temperature] = temp_probabilities
        temp_summary, _ = _build_soft_probability_model_table(
            temp_probabilities,
            offense,
            label=f"offense_soft_pair_t{temperature:.2f}",
            era_bounds=offense_era_bounds,
            mode="pair",
        )
        if not temp_summary.empty:
            temp_summary["temperature"] = temperature
            offense_temperature_summaries.append(temp_summary)

    offense_temperature_summary = (
        pd.concat(offense_temperature_summaries, ignore_index=True)
        if offense_temperature_summaries
        else pd.DataFrame()
    )
    if offense_temperature_summary.empty:
        best_offense_temperature = SOFTMAX_TEMPERATURE
    else:
        ranked = offense_temperature_summary.sort_values(
            [f"{PRIMARY_OUTCOME}_auc", "made_conf_finals_auc", "coverage_mean"],
            ascending=False,
        )
        best_offense_temperature = float(ranked.iloc[0]["temperature"])

    offense_probabilities = offense_probability_frames.get(best_offense_temperature)
    if offense_probabilities is None or offense_probabilities.empty:
        offense_probabilities = _build_probability_frame(
            offense_players,
            cluster_summary_path=OFFENSE_CLUSTER_SUMMARY_PATH,
            feature_cols=OFFENSE_SOFT_FEATURES,
            position_col="archetype_position",
            probability_label="offense_probabilities",
            temperature=best_offense_temperature,
        )
        if not offense_probabilities.empty:
            offense_probabilities = offense_probabilities.rename(columns={"offense_probabilities": "probabilities"})

    offense_presence_summary, offense_presence_scored = _build_logistic_model_table(
        offense,
        label="offense_presence",
        set_col="archetype_set",
        era_bounds=offense_era_bounds,
        mode="presence",
    )
    offense_pair_summary, offense_pair_scored = _build_logistic_model_table(
        offense,
        label="offense_pair",
        set_col="archetype_set",
        era_bounds=offense_era_bounds,
        mode="pair",
    )
    offense_hybrid_summary, offense_hybrid_scored = _build_logistic_model_table(
        offense,
        label="offense_hybrid",
        set_col="archetype_set",
        era_bounds=offense_era_bounds,
        mode="hybrid",
    )

    offense_soft_presence_summary, offense_soft_presence_scored = _build_soft_probability_model_table(
        offense_probabilities,
        offense,
        label=f"offense_soft_presence_t{best_offense_temperature:.2f}",
        era_bounds=offense_era_bounds,
        mode="presence",
    )
    offense_soft_pair_summary, offense_soft_pair_scored = _build_soft_probability_model_table(
        offense_probabilities,
        offense,
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}",
        era_bounds=offense_era_bounds,
        mode="pair",
    )
    offense_soft_hybrid_summary, offense_soft_hybrid_scored = _build_soft_probability_model_table(
        offense_probabilities,
        offense,
        label=f"offense_soft_hybrid_t{best_offense_temperature:.2f}",
        era_bounds=offense_era_bounds,
        mode="hybrid",
    )

    offense_soft_pair_calibrated_scored = _add_era_percentile_score(
        offense_soft_pair_scored,
        score_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_score",
        era_col="era",
        new_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_era_pct",
    )
    offense_soft_pair_calibrated_summary = _baseline_summary(
        offense_soft_pair_calibrated_scored.rename(
            columns={
                f"offense_soft_pair_t{best_offense_temperature:.2f}_era_pct": "score",
            }
        ),
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}_era_pct",
        score_col="score",
    )

    offense_pair_summary_model_summary, offense_pair_summary_scored = _build_pair_summary_model_table(
        offense,
        label="offense_pair_summary",
        set_col="archetype_set",
        era_bounds=offense_era_bounds,
    )

    offense_soft_pair_centroid_summary, offense_soft_pair_centroid_scored = _build_standardized_centroid_combo_table(
        offense_soft_pair_scored,
        offense_pair_scored,
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}_era_centroid",
        era_bounds=modern_era_bounds,
        first_score_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_score",
        second_score_col="offense_pair_score",
    )

    blend_alpha_grid = [round(x / 20.0, 2) for x in range(0, 21)]
    offense_soft_plus_pair_sweep_summary, offense_soft_plus_pair_sweep_scored = _build_standardized_blend_sweep_table(
        offense_soft_pair_scored,
        offense_pair_scored,
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}_plus_pair_sweep",
        era_bounds=offense_era_bounds,
        first_score_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_score",
        second_score_col="offense_pair_score",
        alpha_grid=blend_alpha_grid,
    )
    offense_soft_plus_presence_sweep_summary, offense_soft_plus_presence_sweep_scored = _build_standardized_blend_sweep_table(
        offense_soft_pair_scored,
        offense_presence_scored,
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}_plus_presence_sweep",
        era_bounds=offense_era_bounds,
        first_score_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_score",
        second_score_col="offense_presence_score",
        alpha_grid=blend_alpha_grid,
    )
    offense_soft_plus_pair_summary_sweep_summary, offense_soft_plus_pair_summary_sweep_scored = _build_standardized_blend_sweep_table(
        offense_soft_pair_scored,
        offense_pair_summary_scored,
        label=f"offense_soft_pair_t{best_offense_temperature:.2f}_plus_pair_summary_sweep",
        era_bounds=offense_era_bounds,
        first_score_col=f"offense_soft_pair_t{best_offense_temperature:.2f}_score",
        second_score_col="offense_pair_summary_score",
        alpha_grid=blend_alpha_grid,
    )

    defense_input = defense[defense["defense_archetype_set"].astype(str).ne("UNKNOWN")].copy()
    combined_input = defense[defense["combined_archetype_set"].astype(str).ne("UNKNOWN")].copy()
    defense_input = _attach_targets(defense_input)
    combined_input = _attach_targets(combined_input)

    defense_presence_summary, defense_presence_scored = _build_logistic_model_table(
        defense_input,
        label="defense_presence",
        set_col="defense_archetype_set",
        era_bounds=modern_era_bounds,
        mode="presence",
    )
    defense_pair_summary, defense_pair_scored = _build_logistic_model_table(
        defense_input,
        label="defense_pair",
        set_col="defense_archetype_set",
        era_bounds=modern_era_bounds,
        mode="pair",
    )
    defense_hybrid_summary, defense_hybrid_scored = _build_logistic_model_table(
        defense_input,
        label="defense_hybrid",
        set_col="defense_archetype_set",
        era_bounds=modern_era_bounds,
        mode="hybrid",
    )

    combined_presence_summary, combined_presence_scored = _build_logistic_model_table(
        combined_input,
        label="combined_presence",
        set_col="combined_archetype_set",
        era_bounds=modern_era_bounds,
        mode="presence",
    )
    combined_pair_summary, combined_pair_scored = _build_logistic_model_table(
        combined_input,
        label="combined_pair",
        set_col="combined_archetype_set",
        era_bounds=modern_era_bounds,
        mode="pair",
    )
    combined_hybrid_summary, combined_hybrid_scored = _build_logistic_model_table(
        combined_input,
        label="combined_hybrid",
        set_col="combined_archetype_set",
        era_bounds=modern_era_bounds,
        mode="hybrid",
    )

    modern_window = defense_input[[
        "season",
        "team",
        "playoff_series_wins",
        PRIMARY_OUTCOME,
        "made_finals",
        "won_championship",
    ]].drop_duplicates(subset=["season", "team"]).copy()

    # Baselines on the same modern window.
    baselines = modern_window.copy()
    baselines["wins"] = defense_input.set_index(["season", "team"]).loc[baselines.set_index(["season", "team"]).index, "wins"].values
    baselines["win_pct"] = defense_input.set_index(["season", "team"]).loc[baselines.set_index(["season", "team"]).index, "win_pct"].values
    baselines["playoff_series_wins"] = defense_input.set_index(["season", "team"]).loc[baselines.set_index(["season", "team"]).index, "playoff_series_wins"].values

    model_tables = [
        offense_presence_summary,
        offense_pair_summary,
        offense_hybrid_summary,
        offense_soft_presence_summary,
        offense_soft_pair_summary,
        offense_soft_hybrid_summary,
        offense_soft_pair_calibrated_summary,
        offense_pair_summary_model_summary,
        offense_soft_pair_centroid_summary,
        offense_soft_plus_pair_sweep_summary,
        offense_soft_plus_presence_sweep_summary,
        offense_soft_plus_pair_summary_sweep_summary,
        defense_presence_summary,
        defense_pair_summary,
        defense_hybrid_summary,
        combined_presence_summary,
        combined_pair_summary,
        combined_hybrid_summary,
        _baseline_summary(baselines, label="Wins baseline", score_col="wins"),
        _baseline_summary(baselines, label="Win pct baseline", score_col="win_pct"),
        _baseline_summary(baselines, label="Series wins baseline", score_col="playoff_series_wins"),
    ]
    model_summary = pd.concat(model_tables, ignore_index=True)

    recent_fmvw, recent_note = _recent_fmvw_summary(modern_window)
    team_ops_summary, team_ops_note = _team_ops_summary()

    offense_full_summary = pd.concat(
        [offense_presence_summary, offense_pair_summary, offense_hybrid_summary],
        ignore_index=True,
    )
    best_shape_summary = model_summary[model_summary["label"].isin(
        [
            "offense_presence",
            "offense_pair",
            "offense_hybrid",
            *[label for label in model_summary["label"] if str(label).startswith("offense_soft_")],
            *[label for label in model_summary["label"] if str(label).endswith("_era_centroid")],
            *[label for label in model_summary["label"] if str(label).endswith("_sweep")],
            "offense_pair_summary",
            "defense_presence",
            "defense_pair",
            "defense_hybrid",
            "combined_presence",
            "combined_pair",
            "combined_hybrid",
        ]
    )].sort_values(f"{PRIMARY_OUTCOME}_auc", ascending=False).head(1)

    report_lines = [
        "# Sloan True Comparison Run",
        "",
        "## What This Run Means",
        "",
        "This is the first logistic comparison run for the Sloan paper. It scores team seasons from the existing archive, holds eras out, and compares offense-only, defense-only, and combined two-way shape signals against simple baselines.",
        "The soft-assignment layer now uses nearest-cluster probability distributions over the archetype centroids, so the comparison preserves uncertainty instead of forcing brittle hard labels.",
        "",
        "Important caveat: the defensive archetype layer only exists from 2013-14 onward. That means the fair head-to-head comparison for all three layers is the modern overlap window, while the offense-only layer can also be shown across the full historical archive.",
        "",
        "## Main Comparison",
        "",
        _render_summary_table(model_summary),
        "",
        "## Soft Assignment Comparison",
        "",
        _render_summary_table(
            model_summary[model_summary["label"].str.contains("_soft_")].copy()
        ),
        "",
        "## Era-Calibrated Offense",
        "",
        _render_summary_table(
            model_summary[model_summary["label"].str.contains("_era_pct")].copy()
        ),
        "",
        "## Era-Centroid Combo",
        "",
        _render_summary_table(
            model_summary[model_summary["label"].str.contains("_era_centroid")].copy()
        ),
        "",
        "## Blend Sweeps",
        "",
        _render_summary_table(
            model_summary[model_summary["label"].str.contains("_sweep")].copy()
        ),
        "",
        "## Pair Summary",
        "",
        _render_summary_table(
            model_summary[model_summary["label"].eq("offense_pair_summary")].copy()
        ),
        "",
        "## Offense Temperature Sweep",
        "",
        _temperature_sweep_table(offense_temperature_summary),
        "",
        f"Best offense temperature: {best_offense_temperature:.2f}",
        "",
        "## Reading The Table",
        "",
        "- `CF AUC` is the main Sloan metric because the paper's primary outcome is conference-finals appearance.",
        "- `Finals AUC` and `Title AUC` are secondary outcome checks.",
        "- `Coverage` is the share of archetypes or pairs that were found in the training fold.",
        "",
        "## Best Shape Row",
        "",
        _markdown_table(best_shape_summary, [
            "label",
            "rows",
            f"{PRIMARY_OUTCOME}_auc",
            "made_finals_auc",
            "won_championship_auc",
        ]),
        "",
        "## Full-History Offense Evidence",
        "",
        _render_summary_table(offense_full_summary),
        "",
        _top_examples(offense_hybrid_scored.rename(columns={"offense_hybrid_score": "score"}), "score", "offense hybrid"),
        "",
        _top_examples(combined_hybrid_scored.rename(columns={"combined_hybrid_score": "score"}), "score", "combined hybrid"),
        "",
        "## Recent FMVW Backtest Baseline",
        "",
        recent_note or "",
        "",
    ]
    if not recent_fmvw.empty:
        report_lines.append(_render_summary_table(recent_fmvw))

    report_lines.extend(
        [
            "",
            "## Team Ops Score",
            "",
            team_ops_note or "",
            "",
        ]
    )
    if not team_ops_summary.empty:
        report_lines.append(_render_summary_table(team_ops_summary))

    report_lines.extend(
        [
            "",
        "## Short Readout",
        "",
        "The paper survives if the shape score can separate conference-finals teams better than the simpler baselines, or at least stay competitive while giving a more interpretable roster-shape story.",
        "The hard-label vs nearest-probability ablation is part of that check, not a separate claim.",
        "For the current rerun, the main question is whether the shape layer can better separate conference-finals teams from everyone else.",
            "",
            "The next revision step is to turn the strongest row in this table into the abstract's actual result sentence.",
            "",
        ]
    )

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(report_lines), encoding="utf-8")

    summary = {
        "model_summary": model_summary.to_dict(orient="records"),
        "soft_model_summary": model_summary[model_summary["label"].str.contains("_soft_")].to_dict(orient="records"),
        "era_calibrated_summary": model_summary[model_summary["label"].str.contains("_era_pct")].to_dict(orient="records"),
        "era_centroid_summary": model_summary[model_summary["label"].str.contains("_era_centroid")].to_dict(orient="records"),
        "blend_sweep_summary": model_summary[model_summary["label"].str.contains("_sweep")].to_dict(orient="records"),
        "pair_summary_model_summary": model_summary[model_summary["label"].eq("offense_pair_summary")].to_dict(orient="records"),
        "temperature_sweep": offense_temperature_summary.to_dict(orient="records") if not offense_temperature_summary.empty else [],
        "best_offense_temperature": best_offense_temperature,
        "offense_full_history": offense_full_summary.to_dict(orient="records"),
        "modern_scores_rows": int(len(modern_window)),
        "recent_fmvw": recent_fmvw.to_dict(orient="records") if not recent_fmvw.empty else [],
        "team_ops": team_ops_summary.to_dict(orient="records") if not team_ops_summary.empty else [],
    }
    output_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", default=str(SLOAN_DIR / "comparison-run.md"))
    parser.add_argument("--output-json", default=str(SLOAN_DIR / "comparison-run.json"))
    args = parser.parse_args()

    summary = build_report(
        output_md=Path(args.output_md),
        output_json=Path(args.output_json),
    )
    print(f"Wrote {args.output_md}")
    print(f"Wrote {args.output_json}")
    print(f"Modern comparison rows: {summary['modern_scores_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
