# Public Aggregate Data Schema

The public results bundle contains aggregate team-season artifacts only. It
does not contain player names, player-level projections, historical player
comparisons, raw source feeds, or private operational inputs.

## `team_operations_scores.csv`

One row per NBA team-season; 921 rows covering 1995-96 through 2025-26.

| Column | Meaning |
| --- | --- |
| `season` | NBA season label, such as `1995-96` |
| `team` | Public NBA team abbreviation |
| `wins` | Regular-season wins; comparator/output field, not the target |
| `team_rate_score` | Aggregate roster quality/rate score |
| `team_minutes_coverage` | Aggregate coverage term for roster minutes |
| `team_total_score` | Canonical team-operations structural score |
| `interaction_bonus` | Aggregate roster interaction/fit term |
| `pressure_score` | Aggregate pressure/easy-bucket pressure component |
| `easy_score` | Aggregate easy-bucket creation component |
| `pressure_bonus` | Pressure contribution to the combined score |
| `easy_bonus` | Easy-bucket contribution to the combined score |
| `pressure_easy_bonus` | Combined pressure/easy-bucket contribution |

## `team_season_outcomes.csv`

One row per NBA team-season; 921 rows.

| Column | Meaning |
| --- | --- |
| `season` | NBA season label |
| `team` | Public NBA team abbreviation |
| `wins` | Regular-season wins |
| `made_conf_finals` | Primary outcome: reached the conference finals |
| `made_finals` | Reached the NBA Finals |
| `won_championship` | Won the NBA championship |

Boolean outcomes are encoded as `True`/`False` in the CSV. The modern overlap
window is defined as seasons beginning in 2013-14 or later, yielding 390 rows.

## Reproduction

From the repository root:

```bash
python scripts/bootstrap_sloan_results.py
```

The script writes `results/bootstrap-uncertainty.md` and
`results/bootstrap-uncertainty.json` using the bundled aggregate artifacts.
