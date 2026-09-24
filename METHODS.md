# Methods Summary

DelQuant produces context-neutral player value, cap-adjusted fair market value
(FMV), and FMVW. The Sloan evaluation aggregates those player-level layers into
team roster-construction features representing core, support, fit, interaction,
pressure/easy-bucket creation, and depth.

The primary outcome is conference-finals appearance. The evaluation covers
NBA team-seasons from 1995-96 through 2025-26, with a modern-overlap analysis
beginning in 2013-14. Results are reported as retrospective AUC comparisons
against team-quality baselines. A deterministic row bootstrap with 2,000
iterations provides uncertainty intervals for the fixed score definitions.

Archetype membership is confidence-weighted at cluster boundaries. The
archetype layer is used as an explanatory substrate for roster shape; it is not
presented as a universal championship taxonomy or prospective forecast.

The bundled bootstrap script is self-contained against the sanitized aggregate
artifacts in `results/`. The full comparison implementation remains in the
private internal engine repository and is not required to rerun the headline
bootstrap.
