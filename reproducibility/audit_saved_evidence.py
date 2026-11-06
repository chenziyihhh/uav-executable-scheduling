"""Read-only audit of saved metric logs and quality-certificate dependencies.

This does not regenerate interval enclosures, run protocol experiments, or
certify every local enclosure inclusion. Output files belong to this audit.
Usage: python audit_saved_evidence.py --project PATH --output DIRECTORY
"""
import argparse
import ast
import gzip
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-boundary-step", action="store_true",
                        help="Recompute one 2 ms continuation step per source with the original kernels.")
    args = parser.parse_args()
    base = args.project.resolve()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(base / "src"))
    from e4n10_locked_executor import parameters
    from e4n13_domain_tube import DOMAIN
    from uav_continuation import ContinuedPlan
    from e4n5_wire import encode, decode
    from e4n2_engine import OLD

    checks = []
    inventory = {}

    def record(path, role):
        path = path.resolve()
        key = str(path.relative_to(base)) if path.is_relative_to(base) else str(path)
        key = key.replace("\\", "/")
        if key not in inventory:
            inventory[key] = {"exists": path.is_file(), "roles": []}
            if path.is_file():
                inventory[key].update(bytes=path.stat().st_size, sha256=sha(path))
        if role not in inventory[key]["roles"]:
            inventory[key]["roles"].append(role)
        return inventory[key]

    def check(name, ok, **detail):
        checks.append(dict(name=name, pass_=bool(ok), **detail))

    def binding(name, path, expected):
        actual = record(path, "hash-bound evidence").get("sha256")
        check(name, actual == expected, expected=expected, actual=actual)

    freeze_path = base / "protocol/uav_continuation_freeze.json"
    freeze = read(freeze_path)
    record(freeze_path, "construction freeze")
    for path, digest in freeze["sha256"].items():
        binding("freeze:" + path, base / path, digest)
    checkpoint_lock = base / "protocol/uav_continuation_checkpointing.json"
    checkpointing = read(checkpoint_lock)
    binding("checkpointing parent", freeze_path, checkpointing["parent_sha256"])
    binding("checkpointing script", base / "tests/resume_uav_continuation.py", checkpointing["script_sha256"])

    # Static local-import closure; dynamic source substitutions and data inputs
    # remain separately enumerated, rather than treating AST reachability as proof.
    todo = [base / p for p in freeze["sha256"] if p.endswith(".py")]
    todo += [base / p for p in (
        "tests/check_e4n14_joint_handoff.py",
        "tests/resume_e4n14_joint_handoff.py",
        "tests/resume_e4n14_aggregate_handoff.py",
        "tests/resume_uav_continuation.py",
        "tests/resume_uav_continuation_closed_checkpoint.py",
        "tests/run_uav_continuation_chain.py",
        "tests/audit_uav_continuation_chain.py")]
    seen = set()
    local_imports = []
    while todo:
        p = todo.pop().resolve()
        if p in seen or not p.is_file():
            continue
        seen.add(p)
        record(p, "local Python import closure")
        tree = ast.parse(p.read_text(encoding="utf-8-sig"))
        modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.update(n.name.split(".")[0] for n in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.add(node.module.split(".")[0])
        for module in modules:
            for root in (base / "src", base / "tests", OLD / "src"):
                dep = root / (module + ".py")
                if dep.is_file():
                    local_imports.append([str(p), str(dep)])
                    todo.append(dep)
                    break
    final_freeze_path = base / "protocol/final_guard_confirmation_freeze.json"
    final_freeze = read(final_freeze_path)
    record(final_freeze_path, "later final-comparison freeze")
    for path in seen:
        if path.is_relative_to(base):
            rel = path.relative_to(base).as_posix()
            if rel in final_freeze["sha256"]:
                binding("final comparison: " + rel, path, final_freeze["sha256"][rel])

    cert_dir = base / "results/uav_continuation"
    m = parameters()
    names = ("mass", "g", "B_allocation", "inertia", "w_bias", "w_max_rel",
             "t_min", "t_max", "X_arr", "Y_arr", "K", "L", "eta")
    model = {k: np.asarray(m[k]).tolist() for k in names}
    check("observer gain is exactly 6.5 I", np.array_equal(m["L"], 6.5 * np.eye(12)))
    certificates = []
    initial = []
    for epoch in (0, 25):
        proof_path = cert_dir / f"proof_{epoch:02d}_checkpointed.json"
        quality_path = cert_dir / f"quality_{epoch:02d}.json"
        parent_path = base / f"results/e4n14/joint_{epoch:02d}_aggregate.json"
        parent_cp = base / f"results/e4n14/checkpoint_{epoch:02d}_aggregate.npz"
        cp_path = cert_dir / f"checkpoint_{epoch:02d}_current.npz"
        reference_path = cert_dir / f"reference_{epoch:02d}.npz"
        motion_path = cert_dir / f"motion_{epoch:02d}.npz"
        q, p, parent = read(quality_path), read(proof_path), read(parent_path)
        record(quality_path, "composed quality coefficients")
        for name, path, expected in (
            ("quality proof", proof_path, q["proof_sha256"]),
            ("quality parent", parent_path, q["parent_proof_sha256"]),
            ("quality motion", motion_path, q["motion_sha256"]),
            ("proof reference", reference_path, p["reference_sha256"]),
            ("proof freeze", freeze_path, p["freeze_sha256"]),
            ("proof checkpoint", cp_path, p["current_checkpoint_sha256"]),
            ("proof checkpointing", checkpoint_lock, p["checkpointing_sha256"]),
            ("proof resume", parent_cp, p["resumed_checkpoint_sha256"]),
            ("parent checkpoint", parent_cp, parent["checkpoint_sha256"]),
        ):
            binding(f"epoch {epoch}: {name}", path, expected)
        rows = parent["rows"] + p["rows"]
        check(f"epoch {epoch}: contiguous 2 ms coverage",
              [(r["time_ms"], r["end_ms"]) for r in rows] == [(t, t+2) for t in range(0, 30000, 2)])
        check(f"epoch {epoch}: completion and no reset/reduction",
              p["failure"] is None and p["guaranteed_prefix_ms"] == 30000
              and p["initializations"] == 1 and p["resets"] == 0 and not p["generator_reduction"])
        keys = ("tracking_p", "tracking_v", "estimation_p", "estimation_v")
        values = np.asarray([[r[k] for k in keys] for r in rows])
        check(f"epoch {epoch}: finite nonnegative saved bounds", np.isfinite(values).all() and (values >= 0).all())
        with np.load(reference_path) as a:
            plan = ContinuedPlan.__new__(ContinuedPlan)
            plan.polynomials = a["coefficients"]
            plan.inputs = a["inputs"]
            plan.nodes = a["nodes"]
            plan.hash = p["plan_sha256"]
            plan.epoch, plan.start_ms, plan.end_ms = epoch, 0, 30000
        ref = plan.terms()
        derived = np.r_[np.max(values, axis=0), [ref[k] for k in (
            "reference_acceleration", "reference_kinematic_defect", "position_jump_sum", "velocity_jump_sum")]]
        check(f"epoch {epoch}: coefficient composition",
              np.allclose(derived, q["bounds"], rtol=0, atol=1e-14),
              max_abs_difference=float(np.max(np.abs(derived - q["bounds"]))))
        r0, _ = plan.value(0)
        initial.append(dict(epoch=epoch, state_order="p[3], Euler angles[3], v[3], body angular rates[3]",
                            reference_at_zero=r0.tolist(), plant_box_low=(r0-m["eta"]).tolist(),
                            plant_box_high=(r0+m["eta"]).tolist(),
                            observer_point=r0.tolist(),
                            construction="x_i=r_i(0)+eta_i*xi_i, xi_i in [-1,1]; z=r(0); 12 initial shared generators"))
        with np.load(cp_path) as cp:
            check(f"epoch {epoch}: terminal checkpoint metadata",
                  int(cp["proved_ms"]) == 30000 and str(cp["plan_sha256"]) == p["plan_sha256"])
            shapes = {k: list(cp[k].shape) for k in ("c", "g", "r")}
            check(f"epoch {epoch}: terminal checkpoint finite",
                  all(np.isfinite(cp[k]).all() for k in ("c", "g", "r")) and (cp["r"] >= 0).all())
        with np.load(parent_cp) as cp:
            check(f"epoch {epoch}: parent checkpoint metadata",
                  int(cp["proved_ms"]) == 2800 and str(cp["plan_sha256"]) == parent["plan_sha256"])
            if args.check_boundary_step:
                from e4n11_affine import A, ranges
                from e4n14_affine_kernels import enable
                from e4n11_joint_enclosure import source_command_bound, advance
                from e4n13_correlated_tube import verifier
                from e4n10_prior_enclosure import Box, dynamics, norm_bound
                enable()
                state = [A(c, g, r) for c, g, r in zip(cp["c"], cp["g"], cp["r"])]
                x, z = state[:12], state[12:]
                r, un = plan.value(2800)
                u = source_command_bound(z, r, un, m)
                try:
                    xn, zn, tube, rem = advance(x, z, u, m, order=2)
                except ValueError as exc:
                    if not str(exc).startswith("STATE_TUBE_EXIT"):
                        raise
                    xn, zn, tube, rem = verifier().advance(x, z, u, m, order=2)
                movement = Box(0, (Box(1.)/500).hi)*(dynamics(tube, ranges(u), m)+Box(-m["w_max_rel"], m["w_max_rel"]))
                error = ranges([a-b for a, b in zip(z, x)])-movement
                tracking = tube-plan.range(2800)
                reproduced = [norm_bound(tracking[:3]), norm_bound(tracking[6:9]),
                              norm_bound(error[:3]), norm_bound(error[6:9])]
                target = [p["rows"][0][k] for k in keys]
                check(f"epoch {epoch}: one continuation step 2800--2802 ms",
                      np.allclose(reproduced, target, rtol=0, atol=1e-14)
                      and len(xn[0].g) == p["rows"][0]["generators"],
                      max_abs_difference=float(np.max(np.abs(np.asarray(reproduced)-target))))
        with np.load(motion_path) as motion:
            check(f"epoch {epoch}: motion grids",
                  np.array_equal(motion["full"][:, 0], np.arange(0, 30000, 2))
                  and np.allclose(motion["observed"][:, 0], np.arange(2000, 32001, 2)/1000, rtol=0, atol=1e-13))
        certificates.append(dict(epoch=epoch, rows=len(rows), parent_rows=len(parent["rows"]),
                                 continuation_rows=len(p["rows"]), checkpoint_shapes=shapes,
                                 saved_elapsed_hours=p["elapsed_s"]/3600, coefficients=derived.tolist(),
                                 status_in_saved_proof=p["status"]))

    calpath = OLD / "results_observable/calibration.json"
    cal = read(calpath)
    record(calpath, "runtime codec calibration outside experiment project")
    write(out / "certificate_inputs.json", dict(model=model, initial_conditions=initial,
          domain_low=DOMAIN.lo.tolist(), domain_high=DOMAIN.hi.tolist(),
          physical_step_s=0.002, codec_calibration=cal,
          scope="Declared nonlinear model; parameter export and saved-evidence audit, not a new universal enclosure proof."))

    # Reconstruct receiver estimates from logged successful reassemblies and
    # unchanged source observations/codec. No scheduler or protocol is rerun.
    result_dir = base / "results/final_guard_confirmation"
    summary_path = result_dir / "summary.json"
    summary = read(summary_path)
    record(summary_path, "final comparison reference")
    motions = [np.load(cert_dir / f"motion_{e:02d}.npz") for e in (0, 25)]
    decoded = {}
    for u, data in enumerate(motions):
        a = data["observed"]
        for seq in range(10, 161):
            born = seq * 200 / 1000
            state = np.array([np.interp(born, a[:, 0], a[:, j]) for j in range(1, 7)])
            packet, _ = encode(state, "state", "p13v8", seq*200/1000, u, seq, cal)
            decoded[u, seq] = decode(packet, cal)
    metrics = []
    for row in summary["rows"]:
        tracepath = result_dir / (row["id"] + ".json.gz")
        trace = json.loads(gzip.decompress(tracepath.read_bytes()))
        record(tracepath, "scientific-round event trace")
        events = trace["events"]
        check(row["id"] + ": event chronology", all(a["t"] <= b["t"] for a, b in zip(events, events[1:])))
        delivery = [e for e in events if e["event"] == "delivery"]
        at, current, failed = 0, [None, None], [0, 0]
        for now in range(2200, 32001, 200):
            while at < len(delivery) and delivery[at]["t"] <= now:
                e = delivery[at]
                value = decoded[e["source"], e["seq"]]
                u = e["source"]
                if current[u] is None or value["time"] > current[u]["time"]:
                    current[u] = value
                at += 1
            for u in (0, 1):
                state = current[u]
                if state is None:
                    failed[u] += 1
                    continue
                age = now/1000 - state["time"]
                truth = motions[u]["truth"]
                truth_p = np.array([np.interp(now/1000, truth[:, 0], truth[:, j]) for j in range(1, 4)])
                estimate = state["values"][:3] + age * state["values"][3:]
                failed[u] += int(np.linalg.norm(estimate-truth_p) > 0.5 or age > 0.8+1e-9)
        loss = np.asarray(failed)/150
        distinct = len({(e["source"], e["seq"]) for e in delivery})
        expected = row["result"]
        ok = np.array_equal(loss, expected["task_loss"]) and distinct == expected["complete_deliveries"]
        check(row["id"] + ": metrics", ok)
        metrics.append(dict(id=row["id"], failed_samples=failed, samples_per_source=150,
                            task_loss=loss.tolist(), distinct_completed_updates=distinct, matches_saved=bool(ok)))
    for data in motions:
        data.close()
    audit = dict(utc=datetime.now(timezone.utc).isoformat(), scope="Saved dependency, coefficient and metric audit only",
                 current_audit_environment=dict(python=platform.python_version(), platform=platform.platform(), numpy=np.__version__),
                 checks=checks, check_count=len(checks), failed_checks=[c for c in checks if not c["pass_"]],
                 certificates=certificates, inventory=inventory,
                 local_python_import_edges=local_imports,
                 boundary_step_recomputed=args.check_boundary_step,
                 local_python_files_not_in_primary_freeze=[str(p.relative_to(base)).replace("\\", "/")
                    for p in sorted(seen) if p.is_relative_to(base)
                    and str(p.relative_to(base)).replace("\\", "/") not in freeze["sha256"]],
                 not_performed=["Re-execution of every interval enclosure step",
                                "Independent review of all interval-arithmetic rounding operations",
                                "New protocol experiments or new CPU measurements"],
                 full_rebuild_started=False)
    write(out / "certificate_dependency_audit.json", audit)
    write(out / "metric_replay_audit.json", dict(runs=len(metrics), all_match=all(r["matches_saved"] for r in metrics),
          grid_ms=list(range(2200, 32001, 200)), rows=metrics,
          scope="Independent metric loop over saved successful-reassembly events, using original codec and source motion; not independent packet delivery validation."))
    print(json.dumps(dict(checks=len(checks), failures=audit["failed_checks"], metric_runs=len(metrics),
                          metrics_match=all(r["matches_saved"] for r in metrics),
                          inventory_files=len(inventory), certificates=certificates)))
    if audit["failed_checks"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
