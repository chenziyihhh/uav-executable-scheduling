# Executable Scheduling of Multi-UAV State Updates

Companion materials for **Executable Scheduling of Multi-UAV State Updates under Intermittent Shared Service and Unobservable Local Communication Resources**.

**Authors:** Ziyi Chen, Tian Wang, Houbing Herbert Song, and Anfeng Liu.

This repository provides metric definitions, comparison results, figure data, and quality-certificate documentation for the manuscript. The accompanying experiment archive contains protocol code, saved execution records, and certificate construction artifacts.

- **Repository:** https://github.com/chenziyihhh/uav-executable-scheduling
- **Experiment archive (v1.0):** https://github.com/chenziyihhh/uav-executable-scheduling/releases/tag/v1.0

## Repository Contents

| Path | Contents |
|---|---|
| `reproducibility/METRIC_PROTOCOL.md` | Evaluation grid, event order, communication accounting, CPU measurement boundaries, and aggregation rules. |
| `reproducibility/CERTIFICATE_DEPENDENCIES.md` | Nonlinear quality model, initial sets, validity domain, and certificate construction dependencies. |
| `reproducibility/certificate_inputs.json` | Full-precision model and certificate inputs. |
| `reproducibility/experiment_spec.json` | Frozen evaluation conditions, comparison configurations, and evidence sources. |
| `reproducibility/all_method_costs.csv` | All 160 method–condition outcome and cost rows. |
| `reproducibility/timing_evidence.json` | Recorded execution timing measurements. |
| `reproducibility/metric_replay_audit.json` | Saved metric verification results. |
| `reproducibility/certificate_dependency_audit.json` | Certificate dependency verification records. |
| `reproducibility/audit_saved_evidence.py` | Reconstruction of saved metrics and bounded certificate checks. |
| `reproducibility/PACKAGE_SCOPE.json` | Material scope and reproduction dependencies. |
| `figures/` | Figure data, plotting scripts, and manuscript figures. |
| `docs/GITHUB_UPLOAD_CN.md` | Chinese upload instructions and manuscript wording guidance. |
| `MANIFEST.json` | File sizes and SHA-256 hashes for the packaged repository snapshot. |
| `verify_package.py` | File integrity verification script. |

## Experiment Archive

Download `UAV_Experiment_Evidence.zip` from the **Assets** section of [release v1.0](https://github.com/chenziyihhh/uav-executable-scheduling/releases/tag/v1.0).

The archive contains:

- The 220 inventoried certificate and metric dependency paths.
- Scientific results and timing records associated with the final comparison.
- Local runtime scripts, tests, and protocol configurations.
- Quality-certificate construction inputs and saved artifacts.

Extract the archive into a separate directory and preserve its directory structure. The project path used by the replay command is:

```text
PATH_TO_EXTRACTED_EVIDENCE/
└── UAV_Resource_Certificates_Continuation/
    └── UAV_Resource_Certificates_Continuation/
```

The archive also includes supporting dependencies in sibling directories. Keep these directories in their extracted locations.

## Software Requirements

The figure-generation scripts use Python, NumPy, and Matplotlib. Saved-evidence checks additionally require SciPy.

Install these packages with:

```sh
python -m pip install numpy matplotlib scipy
```

Protocol execution and certificate construction may require additional dependencies specified in the accompanying documentation and scripts.

## Figure Reproduction

From the repository root, run:

```sh
python figures/make_figures.py --data-only --selected quality_profiles paired_cost_frontier communication_ledgers scale_relative
python figures/make_summary_figures.py
```

These commands regenerate the corresponding statistical figures from saved data. The system-model illustration is supplied separately as `figures/system_model.pdf`.

Times New Roman is used when available; otherwise, Matplotlib falls back to DejaVu Serif. Font availability may affect rendering without changing the underlying data.

## Saved-Metric and Certificate Checks

From the repository root, run the following command, replacing `PATH_TO_EXTRACTED_EVIDENCE` with the actual extraction directory:

```sh
python reproducibility/audit_saved_evidence.py --project "PATH_TO_EXTRACTED_EVIDENCE/UAV_Resource_Certificates_Continuation/UAV_Resource_Certificates_Continuation" --output replay_output
```

To additionally recompute the documented 2 ms certificate boundary step, append:

```text
--check-boundary-step
```

The boundary-step check evaluates that documented step. Reconstruction of the full 30 s enclosures requires the construction dependencies and procedures described in `reproducibility/CERTIFICATE_DEPENDENCIES.md`.

Saved-metric replay reconstructs results from recorded evidence. Historical CPU measurements remain measurements of the original execution environment; obtaining new CPU measurements requires executing the corresponding workload in a documented environment.

## Material Scope

The release provides a selected dependency and evidence snapshot supporting the manuscript, including saved comparison results, protocol artifacts, and certificate dependencies.

Original records retain provenance information, including local paths from the experiment environment. Use the extracted archive structure and the dependency documentation to locate packaged files.

The material scope is documented in:

- `reproducibility/PACKAGE_SCOPE.json`
- `reproducibility/CERTIFICATE_DEPENDENCIES.md`
- The experiment archive manifest

Additional historical experiments, external datasets, and inputs used by unrelated tests are outside this snapshot. Consult the relevant script dependencies before running tests beyond the documented replay procedure.

## File Integrity

From the repository root, run:

```sh
python verify_package.py
```

`MANIFEST.json` records the file sizes and SHA-256 hashes of the packaged snapshot. Subsequent documentation edits, including updates to this README, can produce expected differences from that original manifest. Changes to scientific data or code should be tracked explicitly and accompanied by an updated manifest when a new snapshot is released.

## Manuscript Material Links

The repository serves as the entry point for the companion documentation:

https://github.com/chenziyihhh/uav-executable-scheduling

The versioned experiment archive is available at:

https://github.com/chenziyihhh/uav-executable-scheduling/releases/tag/v1.0
