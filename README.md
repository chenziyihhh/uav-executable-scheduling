# Executable scheduling of multi-UAV state updates

Companion materials for **Executable Scheduling of Multi-UAV State Updates under Intermittent Shared Service and Unobservable Local Communication Resources**.

Authors: Ziyi Chen, Tian Wang, Houbing Herbert Song, and Anfeng Liu.

## Repository contents

- `reproducibility/METRIC_PROTOCOL.md`: evaluation grid, event order, accounting, CPU boundaries and aggregation.
- `reproducibility/CERTIFICATE_DEPENDENCIES.md`: nonlinear quality model, initial sets, validity domain and construction dependencies.
- `reproducibility/certificate_inputs.json`: full-precision model and certificate inputs.
- `reproducibility/experiment_spec.json`: frozen conditions, comparison configurations and evidence sources.
- `reproducibility/all_method_costs.csv`: all 160 method/condition outcome and cost rows.
- `reproducibility/timing_evidence.json`: recorded timing evidence.
- `reproducibility/metric_replay_audit.json` and `certificate_dependency_audit.json`: existing verification records.
- `reproducibility/audit_saved_evidence.py`: read-only reconstruction of saved metrics and bounded certificate checks.
- `figures/`: figure inputs, plotting scripts and the manuscript figures.
- `docs/GITHUB_UPLOAD_CN.md`: upload instructions and manuscript wording.
- `MANIFEST.json`: file sizes and SHA-256 hashes for this repository snapshot.

## Figure reproduction

Install Python, NumPy and Matplotlib. From the repository root:

```sh
python figures/make_figures.py --data-only --selected quality_profiles paired_cost_frontier communication_ledgers scale_relative
python figures/make_summary_figures.py
```

Times New Roman is used when installed; otherwise Matplotlib falls back to DejaVu Serif. Figure data are unchanged; host font differences can change rendering.

## Saved-evidence archive

The separate `UAV_Experiment_Evidence.zip` is intended as a repository release asset. It includes the 220 inventoried certificate/metric dependency paths, scientific and timing records of the final comparison, local runtime/test scripts and protocol configurations. Extract it into a separate directory, preserving its layout.

With NumPy and SciPy installed, the saved metric checks can be invoked as:

```sh
python reproducibility/audit_saved_evidence.py --project PATH_TO_EXTRACTED_EVIDENCE/UAV_Resource_Certificates_Continuation/UAV_Resource_Certificates_Continuation --output replay_output
```

Add `--check-boundary-step` only to recompute the documented 2 ms boundary step. This is not a reconstruction of all 30 s enclosures. Historical CPU measurements cannot be recreated by replaying saved metrics. Original frozen records are preserved, including local provenance paths; `PACKAGE_SCOPE.json` and the archive manifest describe the packaged snapshot. The archive is a selected dependency/evidence snapshot, not a complete dump of every historical experiment or external dataset. Unrelated tests may require unbundled inputs.

## Verification

```sh
python verify_package.py
```

Publication status, repository URL, release tag and redistribution license are to be set by the authors. No DOI or repository address is asserted by this preparation package.
