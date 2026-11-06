# Nonlinear quality certificates: dependency and verification map

Scope: the two declared-model 30 s profiles used in the final comparison,
epochs 0 and 25. This map documents construction inputs, saved artifacts and
verification boundaries. It does not extend the certificates to recorded flight.
Paths below are relative to the original experiment project in experiment_spec.json.

## Inputs and executable model

The state is (position[3], Euler angles[3], velocity[3], body angular rates[3]).
At model time zero the reference is r(0); the plant initial set is
x_i(0) = r_i(0) + eta_i xi_i, with each xi_i in [-1,1]. The observer starts at
the point z(0) = r(0). The twelve initial generators preserve these correlations.
The initial plant-box endpoints and r(0) for both epochs are exported in
certificate_inputs.json.

The measurement bounds eta are
(0.00005, 0.00005, 0.00005, 0.000628, 0.000628, 0.000628,
0.0005, 0.0005, 0.0005, 0.00076, 0.00076, 0.00076) in state-component units.
Position is in m, velocity in m/s, angles in rad, and angular rates in rad/s.
The plant has the fixed bias w_bias and componentwise disturbance interval
[-w_max_rel, w_max_rel]. These are full vectors in certificate_inputs.json.
The disturbance need not have a bounded derivative.

Mass is 0.617 kg, gravitational acceleration is 9.8124 m/s², and the inertia
diagonal is (0.00164, 0.00184, 0.003) kg m². Each held actuator input must lie
between 1.3935627 and 1.6335627000000001 N. The controller is
u = u_ref + K(z-r), with K = Y_arr inverse(X_arr); the complete matrices and
allocation matrix are exported without display rounding.

The physical sampling interval is 1/500 s. The digital observer has L = 6.5 I
and is defined by the midpoint of the outward RK4 observer enclosure. Its
floating-point implementation, rather than an unspecified ideal observer,
is the object enclosed by the shared-generator calculation. A separate
numerical trajectory uses four 0.5 ms RK4 plant substeps; it is diagnostic
evidence, not the universal quality proof.

The unchanged admissible domain is:

| Components | Lower | Upper |
| --- | --- | --- |
| x, y position (m) | -4 | 4 |
| z position (m) | 0 | 4 |
| three Euler angles (rad) | -0.1 | 0.1 |
| three velocities (m/s) | -2 | 2 |
| three angular rates (rad/s) | -0.3 | 0.3 |

The enclosure must establish containment inside this domain and the actuator
limits. A proposed tube clipped to the domain is accepted only if its full
image satisfies the required containment condition; clipping alone is not evidence.

## Dependency chain

| Stage | Inputs / code / saved artifact |
| --- | --- |
| Physical and controller parameters | literature/e4n8/offline_design.mat; literature/e4n8/falcon_t.mat; src/e4n10_locked_executor.py |
| Nonlinear dynamics, sampled observer and codec radius | src/e4n9_reference_contract.py; src/e4n10_prior_enclosure.py; src/e4n11_affine.py |
| Joint initial set and 0–2.8 s parent proof | tests/check_e4n14_joint_handoff.py; tests/resume_e4n14_joint_handoff.py; tests/resume_e4n14_aggregate_handoff.py; results/e4n14/joint_00_aggregate.json and joint_25_aggregate.json |
| Parent proof state | results/e4n14/checkpoint_00_aggregate.npz and checkpoint_25_aggregate.npz, at 2,800 ms |
| Reference continuation | src/e4n14_dynamic_reference.py; src/uav_continuation.py; results/uav_continuation/reference_00.npz and reference_25.npz |
| Interval and affine arithmetic | src/e4n10_prior_enclosure.py; src/e4n11_affine.py; src/e4n14_affine_kernels.py; src/e4n14_affine_cache.py |
| Domain and correlated first-exit checks | src/e4n13_domain_tube.py; src/e4n13_correlated_tube.py; src/e4n11_joint_enclosure.py |
| 2.8–30 s continuation and persistence | tests/check_uav_continuation.py; tests/resume_uav_continuation.py; tests/resume_uav_continuation_closed_checkpoint.py |
| Construction/persistence bindings | protocol/uav_continuation_freeze.json; protocol/uav_continuation_checkpointing.json |
| Completed saved bound rows | results/uav_continuation/proof_00_checkpointed.json and proof_25_checkpointed.json |
| Terminal states | results/uav_continuation/checkpoint_00_current.npz and checkpoint_25_current.npz |
| Bound composition and protocol activation | tests/run_uav_continuation_chain.py; src/e4n12_paid_quality.py; quality_00.json and quality_25.json in results/uav_continuation |
| Numerical-motion/arrival audit | tests/run_uav_continuation_motion.py; tests/audit_uav_continuation_chain.py; motion_00.npz and motion_25.npz |
| Codec prerequisite outside the project | UAV_v023_P2_LightReview_FullRun_Package/results_observable/calibration.json and its src/message_codec.py |

The reference preserves the original 2.8 s polynomial prefix, follows the
remaining public targets once and then holds the final target. No trajectory
cycling or state reset is used. Model time [0,30] s corresponds to logical
session time [2,32] s. Runtime admission requires both reserved slots before
the profile end and the applicable received registration; it does not freely
extend validity to later service.

Basic interval operations use numpy.nextafter toward the appropriate infinity.
Trigonometric enclosures use polynomial interval evaluation with a remainder.
Affine operations preserve all generators and add roundoff/remainder radii;
the aggregate kernels use explicit summation/product error allowances.
The cache makes a generator vector read-only after its first norm evaluation.
These implementation rules identify what an independent arithmetic review
must check; enumerating them does not itself verify every rounding operation.

## Composition and saved-record checks

Each profile combines 1,400 parent rows and 13,600 continuation rows: 15,000
adjacent 2 ms intervals covering [0,30] s. The maxima of tracking_p, tracking_v,
estimation_p and estimation_v give Tp, Tv, Ep and Ev. Reference polynomial
bounds give Ar, beta, Jp and Jv. Together with the codec constants, they form
the forward radius in the manuscript. The terminal shared-generator matrix
has shape 24 by 540,012; it contains the plant and observer state at 30 s.

The saved proof status ends with QUALITY_COMPOSITION_PENDING because the
construction and composition are separate stages. quality_00.json and
quality_25.json bind the completed proof, parent proof, numerical-motion file
and reference identity. The audit recomputes the coefficient composition,
rather than treating the status string alone as successful composition.

The primary construction freeze enumerates its direct dependencies, not
every transitive import. certificate_dependency_audit.json records the local
Python import closure, which files are absent from that primary list, and
applicable later final-comparison hash bindings. Being absent from the primary
list is a provenance qualification, not evidence of a changed or missing file.
Static import discovery does not prove the absence of all dynamic dependencies.

The read-only audit checks frozen hashes, coefficient composition, row coverage,
initial/model exports, checkpoint metadata and finite values. With
--check-boundary-step it additionally recomputes the 2,800–2,802 ms continuation
step for each source using the original construction kernels and compares the
four saved bounds and generator count. This is a bounded recurrence check,
not an independently implemented interval verifier.

The numerical chain audit checks saved trajectory samples and arrivals against
the profiles. Its full_proof_checked field refers to those record checks;
it must not be interpreted as re-execution of every universal interval inclusion.

## Decision on full reconstruction

No dependency loss, bound-composition mismatch or metric-replay mismatch has
been found in the completed audit. There is therefore no present need to
regenerate all experiments or both 30 s enclosures merely to complete these
definitions and dependency records. Full reconstruction has not been started.

A stronger goal—an independent end-to-end check of every universal enclosure
step—is not completed by this audit. The saved rows contain summary bounds,
and the rolling checkpoint contains the latest affine state; they are not
a complete collection of every intermediate inclusion witness. That goal
would require rerunning the recurrence from a trusted parent or initial set,
or implementing a verifier with sufficient intermediate witnesses.

Use the following escalation order:

1. Retain this dependency/metric audit and the bounded checkpoint-step check.
2. Review the outward-arithmetic kernels, initial-set definition, domain and
   generation/observer semantics. Resolve any concrete mismatch first.
3. Rebuild only the affected profile if a mismatch changes its bounds or
   trust chain; rerun dependent admissions/results only if those bounds change.
4. If full independent reconstruction is required, isolate its outputs from
   the frozen originals and include parent-prefix construction in the scope.

Recorded 2.8–30 s construction times were 19.7456 h and 17.3342 h, about 37.08 h
combined if run sequentially. These are historical times, exclude additional
review/parent reconstruction work, and are not an estimate guaranteed on the
current host.

The earlier proof_00.json / proof_25.json, reduced proof attempt, failed-replace
checkpoints, handle-repair and recovery records remain in the original project.
They are not substituted for the completed unreduced proof and are not deleted.

## Running the bounded audit

Use Python with NumPy and SciPy, and the intact experiment/legacy projects:

    python audit_saved_evidence.py --project PATH_TO_EXPERIMENT_PROJECT --output AUDIT_OUTPUT --check-boundary-step

The script writes certificate_inputs.json, certificate_dependency_audit.json and
metric_replay_audit.json in AUDIT_OUTPUT. It does not change frozen experimental
artifacts. The manuscript ZIP contains the audit code, parameter export and
reports; large reference/motion/checkpoint arrays and the full runtime remain
in the experiment project and are enumerated, not silently claimed as bundled.
