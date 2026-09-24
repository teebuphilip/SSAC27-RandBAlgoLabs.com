# Sloan Bootstrap Uncertainty Check

This note uses row-resampled bootstrap intervals for AUC. It is an uncertainty check around the fixed score comparison, not a new tuning pass. The score definitions and outcome labels are unchanged.

Bootstrap iterations: 2000; seed: 20270914.

| Window | Score | Outcome | Rows | Base rate | AUC | 95% interval |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 1995-2025 | team_total_score | made_conf_finals | 921 | 13.5% | 75.8% | 71.7%-79.8% |
| 1995-2025 | team_total_score | made_finals | 921 | 6.7% | 79.4% | 74.2%-84.2% |
| 1995-2025 | team_total_score | won_championship | 921 | 3.3% | 81.5% | 74.3%-88.2% |
| 1995-2025 | team_rate_score | made_conf_finals | 921 | 13.5% | 74.7% | 70.5%-78.9% |
| 1995-2025 | team_rate_score | made_finals | 921 | 6.7% | 76.8% | 71.5%-82.0% |
| 1995-2025 | team_rate_score | won_championship | 921 | 3.3% | 77.1% | 69.4%-84.8% |
| 1995-2025 | wins | made_conf_finals | 921 | 13.5% | 90.7% | 87.8%-93.0% |
| 1995-2025 | wins | made_finals | 921 | 6.7% | 88.9% | 85.0%-92.0% |
| 1995-2025 | wins | won_championship | 921 | 3.3% | 91.4% | 86.2%-95.2% |
| 2013-2025 | team_total_score | made_conf_finals | 390 | 13.3% | 79.8% | 74.3%-84.7% |
| 2013-2025 | team_total_score | made_finals | 390 | 6.7% | 83.0% | 76.0%-89.2% |
| 2013-2025 | team_total_score | won_championship | 390 | 3.1% | 83.5% | 71.0%-93.4% |
| 2013-2025 | team_rate_score | made_conf_finals | 390 | 13.3% | 77.0% | 70.7%-82.7% |
| 2013-2025 | team_rate_score | made_finals | 390 | 6.7% | 80.6% | 73.2%-87.6% |
| 2013-2025 | team_rate_score | won_championship | 390 | 3.1% | 79.5% | 67.1%-90.5% |
| 2013-2025 | wins | made_conf_finals | 390 | 13.3% | 90.3% | 86.3%-93.6% |
| 2013-2025 | wins | made_finals | 390 | 6.7% | 88.8% | 83.3%-93.3% |
| 2013-2025 | wins | won_championship | 390 | 3.1% | 92.6% | 85.3%-97.7% |
