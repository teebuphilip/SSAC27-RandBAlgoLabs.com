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

**Stochastic Roster Shape, Archetype Mix, and Championship Likeness in NBA Team Evaluation**

## Contents

- [Abstract](./ABSTRACT.md)
- [Methods](./METHODS.md)
- [Aggregate results](./RESULTS.md)
- [Data disclosure](./DATA-DISCLOSURE.md)
- [Canonical comparison output](./results/comparison-run.md)
- [Bootstrap uncertainty output](./results/bootstrap-uncertainty.md)
- [Comparison script](./scripts/run_sloan_true_comparison.py)
- [Bootstrap script](./scripts/bootstrap_sloan_results.py)

## Reproducibility boundary

This repository contains the submission-facing abstract, methods, aggregate
results, evaluation scripts, and data-disclosure boundary. It intentionally
does not contain raw historical player-comparison archives, raw source CSVs,
restricted upstream feeds, private generated inputs, or operational data.

The full DBB2 engine and broader documentation are maintained at:

<https://github.com/teebuphilip/dbb2-engine>

The results are retrospective discrimination comparisons, not prospective
championship probabilities. Regular-season wins remain the stronger quality
baseline; the team-operations score is presented as an interpretable structural
layer alongside team quality.
