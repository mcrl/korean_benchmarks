"""Regression tests for EQBench emotion-label parsing; no model calls required."""

import runpy
import unittest
from pathlib import Path
from unittest.mock import patch


SCORER_PATH = (
    Path(__file__).resolve().parents[2]
    / "src/custom_tasks/benchmark-compact/ko-eqbench/utils.py"
)
calculate_score_fullscale = runpy.run_path(str(SCORER_PATH))["calculate_score_fullscale"]

# Saved GPT-5.5 response: the old parser rejected "믿지 않음" and returned zero.
REFERENCE = {
    "emotion1": "동정심",
    "emotion2": "믿지 않음",
    "emotion3": "겁먹음",
    "emotion4": "방어적",
    "emotion1_score": 0,
    "emotion2_score": "8",
    "emotion3_score": "3",
    "emotion4_score": "7",
}
RESPONSE = "동정심: 4\n믿지 않음: 6\n겁먹음: 3\n방어적: 9"
EXPECTED_SCORE = 67.61528072809425


def score(response, reference=None):
    if reference is None:
        reference = REFERENCE
    return calculate_score_fullscale(
        {"reference_answer_fullscale": repr(reference)}, [response]
    )


class EQBenchScorerTests(unittest.TestCase):
    def assert_valid_score(self, result, expected=EXPECTED_SCORE):
        self.assertEqual(result["percent_parseable"], 100)
        self.assertAlmostEqual(result["eqbench"], expected, places=12)

    def test_saved_response_with_internal_space(self):
        self.assert_valid_score(score(RESPONSE))

    def test_no_space_labels_keep_the_same_score(self):
        reference = {**REFERENCE, "emotion2": "불신"}
        response = RESPONSE.replace("믿지 않음", "불신")
        self.assert_valid_score(score(response, reference))
        exact_response = "동정심: 0\n불신: 8\n겁먹음: 3\n방어적: 7"
        self.assert_valid_score(score(exact_response, reference), 100)

    def test_spaces_and_tabs_before_colon(self):
        self.assert_valid_score(score(RESPONSE.replace(":", " \t :")))

    def test_internal_tab_matches_identical_reference(self):
        reference = {**REFERENCE, "emotion2": "믿지\t않음"}
        self.assert_valid_score(
            score(RESPONSE.replace("믿지 않음", "믿지\t않음"), reference)
        )

    def test_internal_whitespace_is_not_normalized(self):
        for label in ("믿지  않음", "믿지\t않음"):
            with self.subTest(label=label):
                self.assertEqual(
                    score(RESPONSE.replace("믿지 않음", label)),
                    {"eqbench": 0, "percent_parseable": 0},
                )

    def test_integer_prefix_interpretation_is_unchanged(self):
        self.assert_valid_score(score(RESPONSE.replace(": 4", ": 4.9")))

    def test_invalid_responses_remain_unparseable(self):
        responses = {
            "missing": "\n".join(RESPONSE.splitlines()[:-1]),
            "wrong_emotion": RESPONSE.replace("동정심", "후회"),
            "malformed_separator": RESPONSE.replace("동정심: 4", "동정심 = 4"),
            "malformed_score": RESPONSE.replace("동정심: 4", "동정심: 없음"),
            "extra_emotion": RESPONSE + "\n후회: 1",
        }
        for case, response in responses.items():
            with self.subTest(case=case):
                self.assertEqual(
                    score(response), {"eqbench": 0, "percent_parseable": 0}
                )

    def test_unrelated_multiword_header_remains_ignored(self):
        reference = {
            **REFERENCE,
            "emotion1": "sympathy",
            "emotion2": "disbelief",
            "emotion3": "fear",
            "emotion4": "defensiveness",
        }
        response = "sympathy: 4\ndisbelief: 6\nfear: 3\ndefensiveness: 9"
        self.assert_valid_score(score(response, reference))
        for header in ("Your answer: 5,3,2,1", "Your answer : 5,3,2,1"):
            with self.subTest(header=header):
                self.assert_valid_score(score(response + "\n" + header, reference))
        self.assertEqual(
            score(response + "\nextra: 5", reference),
            {"eqbench": 0, "percent_parseable": 0},
        )

    def test_reference_expressions_are_not_executed(self):
        reference = "print('must not execute') or " + repr(REFERENCE)
        with patch("builtins.print") as output:
            with self.assertRaises(ValueError):
                calculate_score_fullscale(
                    {"reference_answer_fullscale": reference}, [RESPONSE]
                )
            output.assert_not_called()


if __name__ == "__main__":
    unittest.main()
