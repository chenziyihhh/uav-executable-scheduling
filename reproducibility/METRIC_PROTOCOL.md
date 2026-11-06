# Final comparison: metric and timing protocol

This specification documents the saved final-guard comparison. It changes no
measurements or task thresholds. Paths below are relative to the original
experiment project, identified in experiment_spec.json.

## Task loss and delivered updates

The logical session runs from 0 through 32,000 ms. Registration occupies the first
2,000 ms. Each source is evaluated at exactly
T = {2,200, 2,400, ..., 32,000} ms: 150 equally weighted samples.
The sample at 2,000 ms is excluded. The final sample at 32,000 ms is included.
Snapshots are generated at 2,000, 2,200, ..., 31,200 ms, 147 per source.
The code sets last_gen = floor((horizon-800)/200)*200.
This generation cutoff does not shorten the evaluation grid.

At each evaluation instant, use the newest generation timestamp among all
successfully reassembled, decoded updates received by that instant. A duplicate
or an older update does not replace a newer state. If no update has arrived,
the sample fails. Otherwise, with decoded position p, velocity v and generation
time g, the estimate is p + (t-g)v. Compare its Euclidean position error with the
independent plant position, interpolated componentwise using numpy.interp from
the saved truth array. Source observations and truth are separate arrays.

A sample fails if position error > 0.5 m OR age > 0.8 s + 1e-9 s.
The age tolerance is numerical; the position test has no added tolerance.
L_i is the number of failed samples divided by 150; L_max = max_i L_i.
Thus L_i is a sampled failure fraction, not continuous-time violation occupancy.
Continuous model-quality admission is a separate certificate check.

D is the number of distinct (source, sequence) pairs completely reassembled
and decoded during the session. Retransmitted duplicates contribute bytes but
not additional D. The delivery log includes duplicates; its raw length must
not be used as D. “Useful updates” additionally requires a newer generation
timestamp and is a separate counter.

Sources: src/e4n2_engine.py (receiver and metric loop),
src/e4n12_engine.py (registration exclusion and separate truth),
src/mechanism_diagnostics.py (explicit 32,000 ms horizon),
src/e4n5_wire.py and the legacy message_codec.py (quantization/decoding).

## Same-time event order

Each distinct integer-millisecond event time is processed once, in increasing
order. The relevant order within an event is:

1. Apply local quality invalidation; retire leases strictly after their last slot.
2. At a 200 ms boundary, apply capped refill and the observer phase update,
   generate source snapshots when within the generation interval, and enqueue
   an ACK when the 600 ms rule applies after registration. FixedLocal may
   install its local reservation at a 400 ms boundary.
3. Process due downlink grant/ACK arrivals, including the declared loss and
   endpoint validation. Reception changes knowledge; it does not charge again.
4. Process available downlink service, paying queued controls under the guard,
   then considering a new grant according to the configured policy.
5. Process uplink ownership, protected attempts, fallback/retry, quality frames,
   and release receipt/reuse. Update receiver state and causal resource support.
6. Perform independent containment/cost audits and, on T, evaluate the task.

Downlink therefore precedes uplink at a shared timestamp. An ACK guard must
still reserve an uplink obligation due at that same timestamp (now <= slot).
Attempts are charged even when lost. An invalid or incomplete packet is not
a delivered update. See src/ack_prefix_guard.py for the obligation check.

## Cost boundaries

W counts contract-accounted IP frame bytes, including data, grant, ACK and paid
quality frames. Report and release payloads are already inside these frames;
their diagnostic counters are not added again. U counts the actual outer UDP
datagrams recorded by the endpoint transport, including encapsulation. Pipe,
wakeup and shared-memory traffic are local IPC, not additions to W or U.
Unused expired service capacity is neither transmitted bytes nor a byte saving.

The primary C is session_cpu_ms in src/final_guard_udp.py:

- coordinator process CPU from immediately after transport initialization
  through the final in-function receipt/ledger consistency checks;
- plus the active CPU of all three endpoint processes from their ready
  notification to their terminal counters;
- minus separately timed coordinator truth/containment metric-audit regions.

Coordinator and endpoint CPU are measured by time.process_time_ns(), divided
by 1e6. C includes policy construction, online planning, observer/guard work,
code loading, codec, paid-quality activation, IPC handling, local validation
and logging. setup_cpu_ms is the coordinator construction subinterval,
not a separately additive cost. Offline reference/quality construction,
the separate post-run scientific audit, report generation and subsequent
transport.close() cleanup are outside C.

full_stack_cpu_ms is a separately sampled cold boundary: coordinator CPU
starts before transport construction and ends immediately after transport.finish();
endpoint counters are total process CPU since process start. It includes
endpoint interpreter startup/imports. Its coordinator stop occurs before
the final in-function consistency checks included in C. Accordingly, cold
CPU is not algebraically C plus an exactly measured startup term.

wall_ms and per-event wall durations use time.perf_counter_ns().
Per-event durations exclude the timed truth-audit regions and include IPC wait.
Summed multi-process CPU can exceed elapsed wall time. These measurements are
neither energy nor a demonstration that 1 ms physical deadlines are met.

## Repetitions and aggregation

The matrix has 16 service/budget/loss conditions and ten fixed method/penalty
configurations. Three rounds rotate the configuration order. Round 0 provides
scientific outcomes; rounds 1 and 2 repeat timing, with no cross-session planner
cache reuse. The three rounds are not independent service samples.

For each method and condition, use the median of its three CPU observations.
The reported method average is the mean of these 16 medians.
For a paired CPU difference, first subtract reference from exact within each
matched round, then take the median of the three differences. This need not
equal the difference of two medians. For a four-condition budget/loss stratum,
first average paired differences within each round, then report the median
and range of those three round means. The p95 per-event wall statistic pools
all three rounds and selects sorted index floor(0.95*(n-1)).

Task-preserving wins require both L_max <= 0.15, every source loss nonincreasing,
D nondecreasing, and W strictly lower. A dual-ledger win also requires U lower.
A joint win also requires C_exact <= C_reference in every matched round.
All conditions and fixed penalties remain in the comparison.

Source: tests/report_final_guard_confirmation.py.

## Environment provenance

The final matrix freeze is dated 2026-10-23. Nearby saved cost-protocol records
dated 2026-10-22 identify Python 3.12.0, 64-bit AMD64, on
Windows-11-10.0.26200-SP0:

- protocol/uav_confirmation_cost_freeze.json
- results/uav_continuation/observer_cost_protocol.json

These are adjacent provenance, not per-run hardware/environment records for
the final matrix. That matrix did not retain CPU model, affinity, power plan,
external host load, or dependency versions per run. Present-day inventory
cannot retroactively establish them. Existing CPU comparisons retain their
recorded boundaries and repetitions; exact historical wall/CPU reproduction
is not assured. A future timing confirmation should record those fields before
the run and retain the same cost boundaries.

## Read-only replay

Run audit_saved_evidence.py with --project pointing to the original experiment
project and --output to an audit output directory. It reconstructs the metric
loop from the saved scientific-round successful-reassembly events, original
observed/truth motion arrays and original codec. metric_replay_audit.json retains
all 160 results, sample counts and comparisons. It does not independently verify
delivery logs, replay the scheduling policy, or generate new timing observations.
