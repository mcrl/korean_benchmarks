#!/usr/bin/env python3
"""Rescore saved EQBench responses without model calls (dry run unless --apply).

Example:
  python3 rescore_eqbench.py --root /data/Outputs --root /data/outputs_v2 \
      --report-dir /data/rescore-report
  # Inspect runs.csv, then repeat with --apply --backup-dir /data/rescore-backup.

Only EQBench sample metrics and their result means/standard errors are updated.
Merged results are matched to the newest source available at their timestamp.
Unsupported group aggregates, missing samples, and inconsistent old summaries
stop preflight before any original is written. Backups precede all replacements;
ordinary write failures trigger restoration of already replaced originals.
"""
from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import runpy
import stat
import sys
import tempfile
from datetime import datetime, timezone

METRICS = ("eqbench", "percent_parseable")
STAMP = r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+"
SAMPLE_RE = re.compile(rf"samples_(.+)_({STAMP})\.jsonl\Z")
RESULT_RE = re.compile(rf"results_({STAMP})\.json\Z")
MERGED_RE = re.compile(rf"results_merged_({STAMP})\.json\Z")
DEFAULT_SCORER = Path(__file__).resolve().parents[1] / "src/custom_tasks/benchmark-compact/ko-eqbench/utils.py"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def close(a, b):
    return finite(a) and finite(b) and math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)


def mean(values):
    return sum(values) / len(values)


def stderr(values):
    # lm_eval.api.metrics.mean_stderr: sample_stddev(values) / sqrt(n).
    mu = mean(values)
    return math.sqrt(sum((x - mu) ** 2 for x in values) / (len(values) - 1)) / math.sqrt(len(values))


def model_name(result, directory):
    args = result.get("config", {}).get("model_args", {})
    if not isinstance(args, dict):
        args = {}
    return result.get("model_name") or args.get("pretrained") or args.get("model") or directory.name


def check_groups(result, tasks, path):
    """Reject any numeric aggregation in a group containing a changed task."""
    groups = result.get("group_subtasks", {})
    affected = set(tasks)
    while True:
        more = {g for g, members in groups.items() if members and set(members) & affected}
        if more <= affected:
            break
        affected |= more
    for group in affected - set(tasks):
        for section in (result.get("results", {}), result.get("groups", {})):
            node = section.get(group, {})
            if any(key not in {"name", "alias", "sample_len", "samples"} for key in node):
                raise ValueError(f"Unsupported aggregate for affected group {group!r}: {path}")


def preflight(roots, scorer):
    """Read and validate everything, returning changes and per-filter run reports."""
    files = {}
    results = {}
    original_results = {}
    changes = {}
    runs = []
    processed = set()

    def read(path):
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Expected a regular, non-symlink file: {path}")
        if path not in files:
            data = path.read_bytes()
            files[path] = {"data": data, "sha256": digest(data), "mode": stat.S_IMODE(path.stat().st_mode)}
        return files[path]["data"]

    def result(path):
        if path not in results:
            results[path] = json.loads(read(path))
            original_results[path] = copy.deepcopy(results[path])
        return results[path]

    samples = sorted({p for root in roots for p in root.rglob("samples_*eqbench*.jsonl")})
    if not samples:
        raise ValueError("No samples_*eqbench*.jsonl files found")
    for sample_path in samples:
        match = SAMPLE_RE.fullmatch(sample_path.name)
        if not match:
            raise ValueError(f"Unrecognized sample filename: {sample_path}")
        task, timestamp = match.groups()
        result_path = sample_path.with_name(f"results_{timestamp}.json")
        data = result(result_path)
        node = data.get("results", {}).get(task)
        if not isinstance(node, dict):
            raise ValueError(f"Missing task {task!r}: {result_path}")
        check_groups(data, {task}, result_path)
        original = read(sample_path)
        rows = [json.loads(line) for line in original.decode("utf-8").splitlines() if line.strip()]
        if not rows:
            raise ValueError(f"Empty sample file: {sample_path}")
        by_filter = {}
        seen = set()
        changed = 0
        for lineno, row in enumerate(rows, 1):
            filt = row.get("filter")
            if not isinstance(filt, str) or not filt:
                raise ValueError(f"Missing filter: {sample_path}:{lineno}")
            identity = (row.get("doc_id"), filt)
            if identity[0] is None or identity in seen:
                raise ValueError(f"Missing/duplicate doc_id and filter: {sample_path}:{lineno}")
            seen.add(identity)
            response = row.get("filtered_resps")
            if not isinstance(response, list) or len(response) != 1 or not isinstance(response[0], str):
                raise ValueError(f"Expected one saved filtered response: {sample_path}:{lineno}")
            old = {m: row.get(m) for m in METRICS}
            if not all(finite(v) for v in old.values()) or old["percent_parseable"] not in (0, 100):
                raise ValueError(f"Invalid existing metrics: {sample_path}:{lineno}")
            try:
                new = scorer(copy.deepcopy(row["doc"]), list(response))
            except Exception as exc:
                raise ValueError(f"Scorer failed: {sample_path}:{lineno}: {exc}") from exc
            if not isinstance(new, dict) or not all(finite(new.get(m)) for m in METRICS) or new["percent_parseable"] not in (0, 100):
                raise ValueError(f"Scorer returned invalid metrics: {sample_path}:{lineno}")
            is_changed = any(old[m] != new[m] for m in METRICS)
            changed += is_changed
            bucket = by_filter.setdefault(filt, {"old": {m: [] for m in METRICS}, "new": {m: [] for m in METRICS}, "changed": 0})
            bucket["changed"] += is_changed
            for m in METRICS:
                bucket["old"][m].append(old[m])
                bucket["new"][m].append(new[m])
                row[m] = new[m]
        expected_filters = {key.split(",", 1)[1] for key in node if key.startswith("eqbench,")}
        if expected_filters != set(by_filter):
            raise ValueError(f"Result/sample filters do not match: {sample_path}")
        for filt, bucket in by_filter.items():
            count = len(bucket["old"]["eqbench"])
            effective = data.get("n-samples", {}).get(task, {}).get("effective")
            if count < 2 or effective not in (None, count) or node.get("sample_len", count) != count:
                raise ValueError(f"Incomplete sample coverage ({count}, expected {effective}): {sample_path}")
            root = max((r for r in roots if sample_path.is_relative_to(r)), key=lambda p: len(p.parts))
            run = {"sample_path": str(sample_path), "result_path": str(result_path), "task": task, "filter": filt,
                   "model": model_name(data, sample_path.parent), "root": str(root),
                   "prompt_format": str(sample_path.parent.parent.relative_to(root)),
                   "chat_template_present": bool(data.get("chat_template")), "sample_count": count,
                   "changed_samples": bucket["changed"], "unchanged_samples": count - bucket["changed"],
                   "old_parseable_count": sum(v == 100 for v in bucket["old"]["percent_parseable"]),
                   "new_parseable_count": sum(v == 100 for v in bucket["new"]["percent_parseable"])}
            for m in METRICS:
                old_mean, new_mean = mean(bucket["old"][m]), mean(bucket["new"][m])
                key, errkey = f"{m},{filt}", f"{m}_stderr,{filt}"
                if not close(node.get(key), old_mean):
                    raise ValueError(f"Existing mean does not match saved samples: {result_path}: {task}/{key}")
                old_err, new_err = stderr(bucket["old"][m]), stderr(bucket["new"][m])
                if errkey not in node or (node[errkey] != "N/A" and not close(node[errkey], old_err)):
                    raise ValueError(f"Existing stderr does not match saved samples: {result_path}: {task}/{errkey}")
                # Leave insignificant floating point differences untouched on repeat runs.
                if not close(node[key], new_mean):
                    node[key] = new_mean
                if node[errkey] != "N/A" and not close(node[errkey], new_err):
                    node[errkey] = new_err
                run[f"old_{m}"] = old_mean
                run[f"new_{m}"] = new_mean
                run[f"old_{m}_stderr"] = old_err
                run[f"new_{m}_stderr"] = new_err
            runs.append(run)
        if changed:
            changes[sample_path] = ("".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows)).encode("utf-8")
        processed.add((result_path, task))

    merged_count = 0
    # Also inspect sibling results: do not leave a result with missing samples stale.
    for directory in sorted({p.parent for p in samples}):
        source_paths = sorted(p for p in directory.glob("results_*.json") if RESULT_RE.fullmatch(p.name))
        for path in source_paths:
            source = result(path)
            for task in source.get("results", {}):
                if "eqbench" in task and (path, task) not in processed:
                    raise ValueError(f"EQBench result has no matching sample log: {path}: {task}")
        for path in sorted(directory.glob("results_merged_*.json")):
            match = MERGED_RE.fullmatch(path.name)
            if not match:
                raise ValueError(f"Unrecognized merged filename: {path}")
            merged = result(path)
            tasks = [t for t in merged.get("results", {}) if "eqbench" in t]
            if not tasks:
                continue
            check_groups(merged, set(tasks), path)
            for task in tasks:
                candidates = [p for p in source_paths if RESULT_RE.fullmatch(p.name)[1] <= match[1] and task in results[p].get("results", {})]
                if not candidates:
                    raise ValueError(f"No source for merged task: {path}: {task}")
                source_path = candidates[-1]
                old_node = original_results[source_path]["results"][task]
                merged_node = merged["results"][task]
                keys = [k for k in old_node if k.startswith(tuple(m + suffix for m in METRICS for suffix in (",", "_stderr,")))]
                for key in keys:
                    if merged_node.get(key) != old_node[key] and not close(merged_node.get(key), old_node[key]):
                        raise ValueError(f"Merged result differs from latest source: {path}: {task}/{key}")
                    merged_node[key] = results[source_path]["results"][task][key]
            merged_count += 1
    for path, data in results.items():
        if data != original_results[path]:
            changes[path] = encode(data)
    summary = {"sample_logs": len(samples), "sample_count": sum(r["sample_count"] for r in runs),
               "changed_samples": sum(r["changed_samples"] for r in runs),
               "changed_runs": sum(r["changed_samples"] > 0 for r in runs),
               "unchanged_runs": sum(r["changed_samples"] == 0 for r in runs),
               "paired_results": len({p for p, t in processed}), "merged_results": merged_count,
               "changed_files": len(changes)}
    return files, changes, runs, summary


def atomic_write(path, data, mode=0o644):
    """Stage beside destination, fsync, then replace, preserving its permissions."""
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.rescore-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def apply_changes(files, changes, backup_dir, metadata):
    """Back up the complete transaction before writing; restore on write errors."""
    if backup_dir.exists() and any(backup_dir.iterdir()):
        raise ValueError(f"Backup directory must be empty or new: {backup_dir}")
    # Include unchanged inputs: all report/preflight data must still be current.
    for path, info in files.items():
        if digest(path.read_bytes()) != info["sha256"]:
            raise ValueError(f"Input changed since preflight: {path}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest = {**metadata, "status": "backing_up", "files": []}
    for path in sorted(changes):
        backup_path = backup_dir / "originals" / str(path).lstrip(os.sep)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        with backup_path.open("xb") as handle:
            handle.write(files[path]["data"])
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(backup_path, files[path]["mode"])
        if digest(backup_path.read_bytes()) != files[path]["sha256"]:
            raise ValueError(f"Backup verification failed: {backup_path}")
        manifest["files"].append({"path": str(path), "backup_path": str(backup_path), "sha256_before": files[path]["sha256"], "sha256_after": digest(changes[path]), "mode": files[path]["mode"]})
    manifest_path = backup_dir / "manifest.json"
    manifest["status"] = "prepared"
    atomic_write(manifest_path, encode(manifest))
    written = []
    try:
        for path in sorted(changes):
            if digest(path.read_bytes()) != files[path]["sha256"]:
                raise ValueError(f"Original changed before replacement: {path}")
            atomic_write(path, changes[path], files[path]["mode"])
            written.append(path)
        manifest["status"] = "complete"
        atomic_write(manifest_path, encode(manifest))
    except BaseException as exc:
        rollback_errors = []
        for path in reversed(written):
            try:
                atomic_write(path, files[path]["data"], files[path]["mode"])
            except BaseException as rollback_exc:
                rollback_errors.append(f"{path}: {rollback_exc}")
        manifest.update(status="rollback_failed" if rollback_errors else "rolled_back", error=str(exc), rollback_errors=rollback_errors)
        atomic_write(manifest_path, encode(manifest))
        raise
    return manifest_path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", action="append", required=True, type=Path)
    parser.add_argument("--scorer", type=Path, default=DEFAULT_SCORER)
    parser.add_argument("--backup-dir", type=Path)
    parser.add_argument("--report-dir", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="Replace originals after full preflight and verified backups")
    args = parser.parse_args(argv)
    try:
        roots = sorted({p.resolve() for p in args.root})
        if not all(p.is_dir() for p in roots):
            raise ValueError("Every --root must be an existing directory")
        if args.apply and not args.backup_dir:
            raise ValueError("--apply requires --backup-dir")
        for destination in (args.report_dir, args.backup_dir):
            if destination and any(destination.resolve().is_relative_to(root) for root in roots):
                raise ValueError("Report/backup directories must be outside input roots")
        sys.dont_write_bytecode = True
        scorer_path = args.scorer.resolve()
        scorer_bytes = scorer_path.read_bytes()
        scorer = runpy.run_path(str(scorer_path))["calculate_score_fullscale"]
        files, changes, runs, summary = preflight(roots, scorer)
        metadata = {"created_at": datetime.now(timezone.utc).isoformat(), "scorer": str(scorer_path), "scorer_sha256": digest(scorer_bytes), "roots": [str(p) for p in roots], "summary": summary}
        report_dir = args.report_dir.resolve()
        report_dir.mkdir(parents=True, exist_ok=True)
        report = {**metadata, "status": "dry_run", "runs": runs,
                  "files": [{"path": str(p), "sha256_before": files[p]["sha256"], "sha256_after": digest(data)} for p, data in sorted(changes.items())]}
        atomic_write(report_dir / "report.json", encode(report))
        stream = io.StringIO(newline="")
        writer = csv.DictWriter(stream, fieldnames=list(runs[0]))
        writer.writeheader()
        writer.writerows(runs)
        atomic_write(report_dir / "runs.csv", stream.getvalue().encode("utf-8"))
        if args.apply:
            if digest(scorer_path.read_bytes()) != metadata["scorer_sha256"]:
                raise ValueError("Scorer changed during preflight")
            manifest = apply_changes(files, changes, args.backup_dir.resolve(), metadata)
            report.update(status="applied", backup_manifest=str(manifest))
            atomic_write(report_dir / "report.json", encode(report))
        print(json.dumps({"status": report["status"], **summary, "report_dir": str(report_dir)}, ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
