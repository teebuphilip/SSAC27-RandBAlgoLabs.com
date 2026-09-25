# Sloan True Comparison Run

## What This Run Means

This document records the full comparison run supporting the SSAC27 submission. It scores team seasons from the existing archive and compares offense-only, defense-only, and combined two-way shape signals against simple baselines.
The soft-assignment layer now uses nearest-cluster probability distributions over the archetype centroids, so the comparison preserves uncertainty instead of forcing brittle hard labels.

Important caveat: the defensive archetype layer only exists from 2013-14 onward. That means the fair head-to-head comparison for all three layers is the modern overlap window, while the offense-only layer can also be shown across the full historical archive.

## Main Comparison

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_presence | 1995-2025 | 895 | 3 | 57.4% | 59.0% | 61.0% | 1.00 |
| offense_pair | 1995-2025 | 895 | 3 | 54.3% | 60.8% | 61.8% | 0.96 |
| offense_hybrid | 1995-2025 | 895 | 3 | 55.4% | 61.8% | 62.7% | 0.97 |
| offense_soft_presence_t0.65 | 1995-2025 | 921 | 3 | 61.7% | 65.7% | 62.7% | 1.00 |
| offense_soft_pair_t0.65 | 1995-2025 | 921 | 3 | 62.4% | 66.6% | 64.0% | 1.00 |
| offense_soft_hybrid_t0.65 | 1995-2025 | 921 | 3 | 61.7% | 65.7% | 62.7% | 1.00 |
| offense_soft_pair_t0.65_era_pct | 1995-2025 | 921 | 3 | 64.0% | 68.9% | 67.9% | NA |
| offense_pair_summary | 1995-2025 | 895 | 3 | 54.1% | 59.5% | 58.3% | 1.00 |
| offense_soft_pair_t0.65_era_centroid | 2007-2025 | 558 | 2 | 50.4% | 52.3% | 51.6% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 60.5% | 61.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 61.0% | 62.1% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.1% | 61.6% | 62.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.15 | 1995-2025 | 895 | 3 | 55.8% | 62.3% | 63.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.4% | 63.0% | 63.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.0% | 63.6% | 63.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.6% | 64.2% | 64.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.1% | 64.7% | 64.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.7% | 65.0% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.2% | 65.5% | 64.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.6% | 65.8% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.0% | 66.0% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.4% | 66.2% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.6% | 66.3% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.8% | 66.2% | 64.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.75 | 1995-2025 | 895 | 3 | 60.9% | 66.0% | 63.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 65.7% | 63.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 65.3% | 62.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 65.0% | 62.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.5% | 61.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 0.98 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.00 | 1995-2025 | 895 | 3 | 56.9% | 58.6% | 60.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.05 | 1995-2025 | 895 | 3 | 57.3% | 59.1% | 60.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.10 | 1995-2025 | 895 | 3 | 57.7% | 59.6% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.15 | 1995-2025 | 895 | 3 | 58.0% | 60.1% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.20 | 1995-2025 | 895 | 3 | 58.4% | 60.6% | 61.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.25 | 1995-2025 | 895 | 3 | 58.8% | 61.1% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.30 | 1995-2025 | 895 | 3 | 59.2% | 61.7% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.35 | 1995-2025 | 895 | 3 | 59.6% | 62.0% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.40 | 1995-2025 | 895 | 3 | 59.9% | 62.5% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.45 | 1995-2025 | 895 | 3 | 60.2% | 62.9% | 62.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.50 | 1995-2025 | 895 | 3 | 60.5% | 63.3% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.6% | 63.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.8% | 63.8% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.8% | 63.9% | 62.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.9% | 64.1% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.1% | 64.2% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.90 | 1995-2025 | 895 | 3 | 60.9% | 64.3% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.2% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 59.3% | 58.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 59.7% | 58.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.3% | 60.5% | 59.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.15 | 1995-2025 | 895 | 3 | 56.0% | 61.3% | 59.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.7% | 61.8% | 59.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.3% | 62.4% | 60.4% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.8% | 62.9% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.4% | 63.5% | 61.3% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.9% | 64.0% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.4% | 64.6% | 62.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.9% | 65.0% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.4% | 65.4% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.7% | 65.6% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.9% | 65.7% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.70 | 1995-2025 | 895 | 3 | 61.2% | 65.7% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.3% | 65.6% | 62.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.2% | 65.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.2% | 65.2% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 64.8% | 61.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.9% | 64.5% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |
| defense_presence | 2013-2025 | 299 | 2 | 56.0% | 64.3% | 72.9% | 0.98 |
| defense_pair | 2013-2025 | 299 | 2 | 59.2% | 66.1% | 72.2% | 0.83 |
| defense_hybrid | 2013-2025 | 299 | 2 | 58.6% | 66.5% | 72.7% | 0.88 |
| combined_presence | 2013-2025 | 299 | 2 | 53.2% | 58.0% | 63.7% | 0.70 |
| combined_pair | 2013-2025 | 299 | 2 | 56.5% | 61.6% | 69.5% | 0.10 |
| combined_hybrid | 2013-2025 | 299 | 2 | 55.5% | 62.3% | 68.7% | 0.25 |
| Wins baseline | 2013-2025 | 390 | 0 | 90.2% | 88.8% | 92.7% | NA |
| Win pct baseline | 2013-2025 | 390 | 0 | 91.6% | 89.9% | 94.6% | NA |
| Series wins baseline | 2013-2025 | 390 | 0 | 100.0% | 100.0% | 100.0% | NA |

## Soft Assignment Comparison

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_soft_presence_t0.65 | 1995-2025 | 921 | 3 | 61.7% | 65.7% | 62.7% | 1.00 |
| offense_soft_pair_t0.65 | 1995-2025 | 921 | 3 | 62.4% | 66.6% | 64.0% | 1.00 |
| offense_soft_hybrid_t0.65 | 1995-2025 | 921 | 3 | 61.7% | 65.7% | 62.7% | 1.00 |
| offense_soft_pair_t0.65_era_pct | 1995-2025 | 921 | 3 | 64.0% | 68.9% | 67.9% | NA |
| offense_soft_pair_t0.65_era_centroid | 2007-2025 | 558 | 2 | 50.4% | 52.3% | 51.6% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 60.5% | 61.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 61.0% | 62.1% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.1% | 61.6% | 62.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.15 | 1995-2025 | 895 | 3 | 55.8% | 62.3% | 63.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.4% | 63.0% | 63.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.0% | 63.6% | 63.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.6% | 64.2% | 64.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.1% | 64.7% | 64.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.7% | 65.0% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.2% | 65.5% | 64.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.6% | 65.8% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.0% | 66.0% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.4% | 66.2% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.6% | 66.3% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.8% | 66.2% | 64.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.75 | 1995-2025 | 895 | 3 | 60.9% | 66.0% | 63.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 65.7% | 63.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 65.3% | 62.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 65.0% | 62.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.5% | 61.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 0.98 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.00 | 1995-2025 | 895 | 3 | 56.9% | 58.6% | 60.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.05 | 1995-2025 | 895 | 3 | 57.3% | 59.1% | 60.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.10 | 1995-2025 | 895 | 3 | 57.7% | 59.6% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.15 | 1995-2025 | 895 | 3 | 58.0% | 60.1% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.20 | 1995-2025 | 895 | 3 | 58.4% | 60.6% | 61.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.25 | 1995-2025 | 895 | 3 | 58.8% | 61.1% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.30 | 1995-2025 | 895 | 3 | 59.2% | 61.7% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.35 | 1995-2025 | 895 | 3 | 59.6% | 62.0% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.40 | 1995-2025 | 895 | 3 | 59.9% | 62.5% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.45 | 1995-2025 | 895 | 3 | 60.2% | 62.9% | 62.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.50 | 1995-2025 | 895 | 3 | 60.5% | 63.3% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.6% | 63.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.8% | 63.8% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.8% | 63.9% | 62.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.9% | 64.1% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.1% | 64.2% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.90 | 1995-2025 | 895 | 3 | 60.9% | 64.3% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.2% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 59.3% | 58.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 59.7% | 58.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.3% | 60.5% | 59.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.15 | 1995-2025 | 895 | 3 | 56.0% | 61.3% | 59.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.7% | 61.8% | 59.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.3% | 62.4% | 60.4% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.8% | 62.9% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.4% | 63.5% | 61.3% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.9% | 64.0% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.4% | 64.6% | 62.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.9% | 65.0% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.4% | 65.4% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.7% | 65.6% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.9% | 65.7% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.70 | 1995-2025 | 895 | 3 | 61.2% | 65.7% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.3% | 65.6% | 62.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.2% | 65.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.2% | 65.2% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 64.8% | 61.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.9% | 64.5% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |

## Era-Calibrated Offense

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_soft_pair_t0.65_era_pct | 1995-2025 | 921 | 3 | 64.0% | 68.9% | 67.9% | NA |

## Era-Centroid Combo

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_soft_pair_t0.65_era_centroid | 2007-2025 | 558 | 2 | 50.4% | 52.3% | 51.6% | 0.98 |

## Blend Sweeps

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 60.5% | 61.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 61.0% | 62.1% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.1% | 61.6% | 62.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.15 | 1995-2025 | 895 | 3 | 55.8% | 62.3% | 63.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.4% | 63.0% | 63.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.0% | 63.6% | 63.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.6% | 64.2% | 64.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.1% | 64.7% | 64.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.7% | 65.0% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.2% | 65.5% | 64.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.6% | 65.8% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.0% | 66.0% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.4% | 66.2% | 65.0% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.6% | 66.3% | 64.7% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.8% | 66.2% | 64.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.75 | 1995-2025 | 895 | 3 | 60.9% | 66.0% | 63.9% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 65.7% | 63.4% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 65.3% | 62.8% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 65.0% | 62.2% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.5% | 61.5% | 0.98 |
| offense_soft_pair_t0.65_plus_pair_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 0.98 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.00 | 1995-2025 | 895 | 3 | 56.9% | 58.6% | 60.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.05 | 1995-2025 | 895 | 3 | 57.3% | 59.1% | 60.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.10 | 1995-2025 | 895 | 3 | 57.7% | 59.6% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.15 | 1995-2025 | 895 | 3 | 58.0% | 60.1% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.20 | 1995-2025 | 895 | 3 | 58.4% | 60.6% | 61.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.25 | 1995-2025 | 895 | 3 | 58.8% | 61.1% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.30 | 1995-2025 | 895 | 3 | 59.2% | 61.7% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.35 | 1995-2025 | 895 | 3 | 59.6% | 62.0% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.40 | 1995-2025 | 895 | 3 | 59.9% | 62.5% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.45 | 1995-2025 | 895 | 3 | 60.2% | 62.9% | 62.3% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.50 | 1995-2025 | 895 | 3 | 60.5% | 63.3% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.6% | 63.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.8% | 63.8% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.8% | 63.9% | 62.4% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.70 | 1995-2025 | 895 | 3 | 60.9% | 64.1% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.1% | 64.2% | 62.0% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.9% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.0% | 64.2% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.90 | 1995-2025 | 895 | 3 | 60.9% | 64.3% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.8% | 64.2% | 61.2% | 1.00 |
| offense_soft_pair_t0.65_plus_presence_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.00 | 1995-2025 | 895 | 3 | 54.0% | 59.3% | 58.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.05 | 1995-2025 | 895 | 3 | 54.5% | 59.7% | 58.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.10 | 1995-2025 | 895 | 3 | 55.3% | 60.5% | 59.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.15 | 1995-2025 | 895 | 3 | 56.0% | 61.3% | 59.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.20 | 1995-2025 | 895 | 3 | 56.7% | 61.8% | 59.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.25 | 1995-2025 | 895 | 3 | 57.3% | 62.4% | 60.4% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.30 | 1995-2025 | 895 | 3 | 57.8% | 62.9% | 60.9% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.35 | 1995-2025 | 895 | 3 | 58.4% | 63.5% | 61.3% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.40 | 1995-2025 | 895 | 3 | 58.9% | 64.0% | 61.7% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.45 | 1995-2025 | 895 | 3 | 59.4% | 64.6% | 62.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.50 | 1995-2025 | 895 | 3 | 59.9% | 65.0% | 62.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.55 | 1995-2025 | 895 | 3 | 60.4% | 65.4% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.60 | 1995-2025 | 895 | 3 | 60.7% | 65.6% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.65 | 1995-2025 | 895 | 3 | 60.9% | 65.7% | 63.1% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.70 | 1995-2025 | 895 | 3 | 61.2% | 65.7% | 63.0% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.75 | 1995-2025 | 895 | 3 | 61.3% | 65.6% | 62.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.80 | 1995-2025 | 895 | 3 | 61.2% | 65.5% | 62.6% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.85 | 1995-2025 | 895 | 3 | 61.2% | 65.2% | 62.2% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.90 | 1995-2025 | 895 | 3 | 61.0% | 64.8% | 61.8% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a0.95 | 1995-2025 | 895 | 3 | 60.9% | 64.5% | 61.5% | 1.00 |
| offense_soft_pair_t0.65_plus_pair_summary_sweep_a1.00 | 1995-2025 | 895 | 3 | 60.7% | 64.2% | 60.9% | 1.00 |

## Pair Summary

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_pair_summary | 1995-2025 | 895 | 3 | 54.1% | 59.5% | 58.3% | 1.00 |

## Offense Temperature Sweep

| temperature | label | made_conf_finals_auc | made_finals_auc | coverage_mean |
| --- | --- | --- | --- | --- |
| 0.50 | offense_soft_pair_t0.50 | 61.8% | 66.6% | 1.00 |
| 0.65 | offense_soft_pair_t0.65 | 62.4% | 66.6% | 1.00 |
| 0.75 | offense_soft_pair_t0.75 | 62.4% | 66.3% | 1.00 |

Best offense temperature: 0.65

## Reading The Table

- `CF AUC` is the main Sloan metric because the paper's primary outcome is conference-finals appearance.
- `Finals AUC` and `Title AUC` are secondary outcome checks.
- `Coverage` is the share of archetypes or pairs that were found in the training fold.

## Best Shape Row

| label | rows | made_conf_finals_auc | made_finals_auc | won_championship_auc |
| --- | --- | --- | --- | --- |
| offense_soft_pair_t0.65_era_pct | 921 | 0.6400 | 0.6889 | 0.6787 |

## Full-History Offense Evidence

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| offense_presence | 1995-2025 | 895 | 3 | 57.4% | 59.0% | 61.0% | 1.00 |
| offense_pair | 1995-2025 | 895 | 3 | 54.3% | 60.8% | 61.8% | 0.96 |
| offense_hybrid | 1995-2025 | 895 | 3 | 55.4% | 61.8% | 62.7% | 0.97 |

### Top 8 offense hybrid rows

| season | team | score | made_conf_finals | made_finals | won_championship |
| --- | --- | --- | --- | --- | --- |
| 2018-19 | PHI | 0.9767 | N | N | N |
| 2021-22 | MIL | 0.9377 | N | N | N |
| 2001-02 | MIL | 0.9180 | N | N | N |
| 1995-96 | CHI | 0.9150 | Y | Y | Y |
| 2015-16 | CHI | 0.8804 | N | N | N |
| 2022-23 | LAL | 0.8696 | Y | N | N |
| 2005-06 | LAL | 0.8670 | N | N | N |
| 2025-26 | MIL | 0.8623 | N | N | N |

### Top 8 combined hybrid rows

| season | team | score | made_conf_finals | made_finals | won_championship |
| --- | --- | --- | --- | --- | --- |
| 2017-18 | MIL | 0.6231 | N | N | N |
| 2014-15 | GSW | 0.5866 | Y | Y | Y |
| 2019-20 | LAC | 0.5299 | N | N | N |
| 2018-19 | OKC | 0.5016 | N | N | N |
| 2017-18 | OKC | 0.4817 | N | N | N |
| 2021-22 | MIL | 0.4619 | N | N | N |
| 2018-19 | NOP | 0.4605 | N | N | N |
| 2019-20 | NOP | 0.4560 | N | N | N |

## Recent FMVW Backtest Baseline



| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| FMVW predicted wins | 2021-22 to 2025-26 | 150 | 5 | 69.3% | 61.4% | 50.3% | NA |
| FMVW team FMV total | 2021-22 to 2025-26 | 150 | 5 | 69.3% | 61.4% | 50.3% | NA |

## Team Ops Score


The team-operations score is evaluated as a retrospective discriminator over the full archive without era hold-out; the archetype-only models above use era-held-out evaluation.

| Model | Window | Rows | Eras | CF AUC | Finals AUC | Title AUC | Coverage |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Team ops total score | 1995-96 to 2025-26 | 921 | 31 | 75.8% | 79.4% | 81.5% | NA |
| Team ops total score (modern) | 2013-14 to 2025-26 | 390 | 13 | 79.8% | 83.0% | 83.5% | NA |
| Team rate score | 1995-96 to 2025-26 | 921 | 31 | 74.7% | 76.8% | 77.1% | NA |
| Pressure score | 1995-96 to 2025-26 | 921 | 31 | 61.3% | 63.3% | 71.7% | NA |
| Easy score | 1995-96 to 2025-26 | 921 | 31 | 73.7% | 74.8% | 74.3% | NA |
