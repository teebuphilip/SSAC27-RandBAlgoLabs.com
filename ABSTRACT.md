# Stochastic Roster Shape, Archetype Mix, and Championship Likeness in NBA Team Evaluation

**Introduction.**

We test whether elite basketball evaluation can be translated into a reproducible roster-construction framework. DBB2 converts context-neutral player value into cap-adjusted FMV and then into FMVW, then layers in offensive and defensive archetype structure to represent how value is distributed across a roster. The goal is not to replace player value, but to test whether the way value is arranged on a team carries additional postseason signal.

**Methods.**

Using NBA seasons from 1995-96 through 2025-26, we build era-aware championship reference sets and compare historical team shapes against conference-finals, Finals, and title outcomes. The defensive layer adds a separate reproducible axis, and the modern offense-plus-defense crosswalk preserves uncertainty at archetype boundaries through confidence-weighted membership.

**Results.**

The strongest current structural result comes from a broader roster-construction score that splits team value into core, support, fit, interaction, pressure/easy-bucket, and depth terms. That score reaches 75.8% conference-finals AUC overall and 79.8% in the modern window, with bootstrap intervals of 71.7%-79.8% and 74.3%-84.7%, respectively. Regular-season wins remain a stronger quality baseline, so we interpret this result as structural and explanatory rather than as a claim to replace wins.

**Conclusion.**

These roster-construction signals provide an interpretable structural readout alongside simpler baselines such as raw FMV aggregation, FMVW without archetype conditioning, wins, net rating, and top-7 talent sum. The contribution is a calibrated roster-shape method linking player value, archetype structure, and postseason team outcomes while preserving uncertainty at archetype boundaries.
