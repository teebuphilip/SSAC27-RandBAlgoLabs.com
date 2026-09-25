# Roster Shape, Archetype Structure, and Postseason Signal in NBA Team Evaluation

**Introduction.**

We test whether the structural arrangement of value across a roster carries postseason signal beyond player-value totals. We convert context-neutral player value into cap-adjusted fair market value (FMV) and wins-equivalent FMVW, then decompose team rosters to represent how value is concentrated, paired, and supported. The goal is not to replace team-quality measures, but to test whether roster shape carries additional conference-finals discrimination.

**Methods.**

Using NBA team-seasons from 1995-96 through 2025-26 (921 team-seasons), we construct a team-operations score from DelQuant (www.delquant.com) player-value projections aggregated across each roster. The score decomposes roster value into six components: core-value concentration, supporting-cast value, archetype fit, interaction effects, pressure and easy-bucket creation, and depth. Current-season wins are not a score input. Archetype assignments use separate offensive and defensive archives, with nearest-cluster probabilities used for the archetype-only comparisons; the team-operations score is evaluated as a retrospective discriminator over the full archive without era hold-out. A deterministic row bootstrap with 2,000 iterations and fixed seed provides uncertainty intervals.

**Results.**

The team-operations score reaches 75.8% conference-finals AUC over the full archive (95% CI: 71.7%-79.8%, n=921) and 79.8% in the modern window from 2013-14 onward (95% CI: 74.3%-84.7%, n=390). Regular-season wins remain the stronger quality baseline at 90.7% overall and 90.3% in the modern window. We present these results as retrospective discrimination evidence, not prospective championship probabilities, and interpret the structural score as complementary to rather than competitive with wins.

**Conclusion.**

A decomposed roster-construction score provides an interpretable structural readout alongside established baselines including raw FMV aggregation, FMVW without archetype conditioning, wins, net rating, and top-7 talent sum. The main contribution is a calibrated method linking player-value distribution, archetype structure, and postseason team outcomes. The methods are implemented in the DelQuant (www.delquant.com) sports-analytics platform from R & B AlgoLabs, which provides the applied decision-support context for this work.
