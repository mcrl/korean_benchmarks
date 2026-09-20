"""Transaction and aggregation tests; no model or network calls."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("rescore_eqbench", Path(__file__).with_name("rescore_eqbench.py"))
rescore = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rescore)
TASK = "ko-eqbench"
STAMP = "2026-06-07T15-53-24.082830"


def score(doc, responses):
    return {"eqbench": float(responses[0]), "percent_parseable": 100}


class RescoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "outputs"
        self.model = self.root / "chat" / "model"
        self.model.mkdir(parents=True)
        self.samples = self.model / f"samples_{TASK}_{STAMP}.jsonl"
        self.result = self.model / f"results_{STAMP}.json"
        self.rows = [{"doc_id": i, "doc": {"reference_answer_fullscale": "{}", "prompt": "raw"}, "resps": [[str(value)]], "filtered_resps": [str(value)], "filter": "none", "metrics": ["eqbench", "percent_parseable"], "eqbench": 0, "percent_parseable": 0, "unrelated": {"nested": i}} for i, value in enumerate((60, 80))]
        self.samples.write_text("".join(json.dumps(r) + "\n" for r in self.rows))
        self.data = {"results": {TASK: {"alias": TASK, "eqbench,none": 0, "eqbench_stderr,none": 0, "percent_parseable,none": 0, "percent_parseable_stderr,none": 0, "sample_len": 2}, "other-task": {"acc,none": 0.5}}, "n-samples": {TASK: {"effective": 2}}, "group_subtasks": {"group": [TASK, "other-task"]}, "config": {"model_args": {"model": "provider/model"}}}
        self.result.write_text(json.dumps(self.data))

    def preflight(self):
        return rescore.preflight([self.root], score)

    def test_preflight_preserves_responses_and_unrelated_metrics(self):
        before = self.samples.read_bytes()
        files, changes, runs, summary = self.preflight()
        self.assertEqual(self.samples.read_bytes(), before)
        rows = [json.loads(s) for s in changes[self.samples].splitlines()]
        for old, new in zip(self.rows, rows):
            self.assertEqual({k: v for k, v in old.items() if k not in rescore.METRICS}, {k: v for k, v in new.items() if k not in rescore.METRICS})
        result = json.loads(changes[self.result])
        self.assertEqual(result["results"]["other-task"], self.data["results"]["other-task"])
        self.assertEqual(result["results"][TASK]["eqbench,none"], 70)
        self.assertAlmostEqual(result["results"][TASK]["eqbench_stderr,none"], 10)
        self.assertEqual(runs[0]["new_parseable_count"], 2)
        self.assertEqual(runs[0]["model"], "provider/model")
        self.assertEqual(summary["changed_samples"], 2)

    def test_apply_backups_permissions_and_idempotence(self):
        os.chmod(self.samples, 0o640)
        files, changes, _, _ = self.preflight()
        backup = self.base / "backup"
        manifest_path = rescore.apply_changes(files, changes, backup, {})
        manifest = json.loads(manifest_path.read_text())
        self.assertEqual(manifest["status"], "complete")
        for entry in manifest["files"]:
            original = Path(entry["backup_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(original).hexdigest(), entry["sha256_before"])
            self.assertEqual(hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest(), entry["sha256_after"])
        self.assertEqual(self.samples.stat().st_mode & 0o777, 0o640)
        _, new_changes, _, summary = self.preflight()
        self.assertEqual(new_changes, {})
        self.assertEqual(summary["changed_samples"], 0)

    def test_missing_pair_and_incomplete_sample_fail_before_writes(self):
        self.result.unlink()
        with self.assertRaises(ValueError):
            self.preflight()
        self.data["n-samples"][TASK]["effective"] = 3
        self.result.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, "Incomplete sample"):
            self.preflight()

    def test_existing_mean_mismatch_fails(self):
        self.data["results"][TASK]["eqbench,none"] = 7
        self.result.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, "Existing mean"):
            self.preflight()

    def test_group_metric_rejected(self):
        self.data["results"]["group"] = {"score,none": 0.2}
        self.result.write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError, "Unsupported aggregate"):
            self.preflight()

    def test_merged_result_updated_and_mismatch_rejected(self):
        merged = self.model / "results_merged_2026-06-08T17-56-43.483129.json"
        merged.write_text(json.dumps(self.data))
        _, changes, _, summary = self.preflight()
        self.assertEqual(json.loads(changes[merged])["results"][TASK]["eqbench,none"], 70)
        self.assertEqual(summary["merged_results"], 1)
        bad = copy.deepcopy(self.data)
        bad["results"][TASK]["eqbench,none"] = 17
        merged.write_text(json.dumps(bad))
        with self.assertRaisesRegex(ValueError, "Merged result differs"):
            self.preflight()

    def test_input_changed_after_preflight_prevents_apply(self):
        files, changes, _, _ = self.preflight()
        self.samples.write_text(self.samples.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "Input changed"):
            rescore.apply_changes(files, changes, self.base / "backup", {})
        self.assertEqual(json.loads(self.result.read_text())["results"][TASK]["eqbench,none"], 0)

    def test_write_failure_restores_written_originals(self):
        files, changes, _, _ = self.preflight()
        backup = self.base / "backup"
        real_write = rescore.atomic_write
        failed = False

        def fail_second_original(path, data, mode=0o644):
            nonlocal failed
            if path == self.samples and not failed:
                failed = True
                raise OSError("simulated disk failure")
            return real_write(path, data, mode)

        with mock.patch.object(rescore, "atomic_write", side_effect=fail_second_original):
            with self.assertRaisesRegex(OSError, "disk failure"):
                rescore.apply_changes(files, changes, backup, {})
        for path, info in files.items():
            self.assertEqual(path.read_bytes(), info["data"])
        self.assertEqual(json.loads((backup / "manifest.json").read_text())["status"], "rolled_back")

    def test_cli_defaults_to_dry_run(self):
        scorer = self.base / "scorer.py"
        scorer.write_text('def calculate_score_fullscale(doc, responses):\n    return {"eqbench": float(responses[0]), "percent_parseable": 100}\n')
        before = self.samples.read_bytes()
        report = self.base / "report"
        result = rescore.main(["--root", str(self.root), "--scorer", str(scorer), "--report-dir", str(report)])
        self.assertEqual(result, 0)
        self.assertEqual(self.samples.read_bytes(), before)
        self.assertEqual(json.loads((report / "report.json").read_text())["status"], "dry_run")
        self.assertTrue((report / "runs.csv").exists())


if __name__ == "__main__":
    unittest.main()
