# Executable Scheduling of Multi-UAV State Updates

Companion materials for **Executable Scheduling of Multi-UAV State Updates under Intermittent Shared Service and Unobservable Local Communication Resources**.

Authors: Ziyi Chen, Tian Wang, Houbing Herbert Song, and Anfeng Liu.

Repository: https://github.com/chenziyihhh/uav-executable-scheduling

Experiment archive: https://github.com/chenziyihhh/uav-executable-scheduling/releases

## Contents

`figures/` contains final plotting scripts, saved inputs, and manuscript figures. `reproducibility/` contains metric definitions, all 160 method-condition outcomes, model inputs, frozen specifications, and certificate dependency documentation.

## Figure reproduction

```sh
python -m pip install numpy matplotlib scipy
python figures/make_figures.py --data-only --selected quality_profiles paired_cost_frontier communication_ledgers scale_relative
python figures/make_summary_figures.py
```

The system model is supplied as a PDF. Fonts depend on the local installation.

## Saved-result reproduction

Download UAV_Experiment_Evidence.zip from Releases and preserve the extracted directory layout. From this repository run:

```sh
python reproducibility/audit_saved_evidence.py --project "PATH_TO_EXTRACTED_EVIDENCE/UAV_Resource_Certificates_Continuation/UAV_Resource_Certificates_Continuation" --output replay_output
```

The archive contains the final comparison records and selected protocol and certificate dependencies. Existing module names are retained to preserve imports and recorded hashes. Required construction and checking scripts may reside under `tests/`.

The documented command reads saved records; it does not run a new protocol experiment. Optional `--check-boundary-step` recomputes the documented 2 ms step. Full enclosure construction and new timing measurements require the conditions and dependencies documented in reproducibility/CERTIFICATE_DEPENDENCIES.md and METRIC_PROTOCOL.md. External service datasets are not included.

## Integrity

```sh
python verify_package.py
```

MANIFEST.json covers this repository snapshot. EVIDENCE_MANIFEST.json covers the release archive. Update the corresponding manifest when files are changed.
