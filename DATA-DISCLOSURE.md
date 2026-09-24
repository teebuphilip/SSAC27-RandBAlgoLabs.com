# Data and Artifact Disclosure

The public repository exposes the evaluation scripts, model documentation,
schemas, aggregate result artifacts, and a sanitized team-season score/outcome
table sufficient to rerun the headline bootstrap.

This repository does not include raw historical player-comparison archives,
player-level source CSVs, restricted upstream feeds, private generated inputs,
or operational data. Those materials remain subject to their original licenses
and access controls.

The aggregate result tables here are sufficient to inspect the submission
claim, and `scripts/bootstrap_sloan_results.py` runs against the bundled
sanitized aggregate artifacts. The full internal comparison runner requires
additional authorized source artifacts that are not redistributed here.
