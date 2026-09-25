# SSAC27 — R & B AlgoLabs

Submission materials for the 2027 MIT Sloan Sports Analytics Conference
Research Paper Competition.

## Authors

- **Teebu Philip**
- R & B AlgoLabs
- Miramar, FL 33027
- <https://www.randbalgolabs.com>
- Contact: <teebu@randbalgolabs.com>

## Paper

**Roster Shape, Archetype Structure, and Postseason Signal in NBA Team Evaluation**

## Contents

- [Abstract](./ABSTRACT.md)
- [Methods](./METHODS.md)
- [Aggregate results](./RESULTS.md)
- [Data disclosure](./DATA-DISCLOSURE.md)
- [Acknowledgment and commercial disclosure](./ACKNOWLEDGMENT.md)
- [Canonical comparison output](./results/comparison-run.md)
- [Bootstrap uncertainty output](./results/bootstrap-uncertainty.md)
- [Sanitized team-operation scores](./results/comparison_summary_sanitized.json)
- [Team-operation scores CSV](./results/team_operations_scores.csv)
- [Sanitized team-season outcomes](./results/team_season_outcomes.csv)
- [Aggregate data schema](./results/SCHEMA.md)
- [Bootstrap script](./scripts/bootstrap_sloan_results.py)

## Reproducibility boundary

This repository contains the submission-facing abstract, methods, aggregate
results, sanitized team-season artifacts, evaluation scripts, and data-
disclosure boundary. It intentionally does not contain raw historical player-
comparison archives, player-level source CSVs, restricted upstream feeds,
private generated inputs, or operational data.

The full comparison implementation is maintained in the private internal
engine repository and is not part of this public-facing submission package.
The bundled bootstrap script is self-contained against the sanitized aggregate
artifacts in `results/`. From the repository root, run
`python -m pip install -r requirements.txt` once, then run
`python scripts/bootstrap_sloan_results.py` to regenerate the bootstrap
artifacts.

The results are retrospective discrimination comparisons, not prospective
championship probabilities. Regular-season wins remain the stronger quality
baseline; the team-operations score is presented as an interpretable structural
layer alongside team quality.
