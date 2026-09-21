import json

from scripts.generate_results import ROOT, generate_all


EXPECTED_COUNTS = {
    "comvita_kids_herbal_syrup.json": 19,
    "arepa_brain_drink.json": 23,
    "seed_am_02.json": 29,
}


def test_generated_results_are_stable_and_traceable(tmp_path):
    paths = generate_all(tmp_path)

    assert {path.name for path in paths} == set(EXPECTED_COUNTS)

    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))

        assert data["stable"] is True
        assert len(data["runs"]) == 2

        run_1 = data["runs"][0]["claims"]
        run_2 = data["runs"][1]["claims"]

        assert run_1 == run_2
        assert len(run_1) == EXPECTED_COUNTS[path.name]

        for claim in run_1:
            assert claim["verdict"] in {"green", "amber", "red"}
            assert claim["reason"]
            assert claim["rule_id"]
            assert claim["authority"]
            assert claim["source"] is not None
            assert claim["source"]["document"] == "Sources & Logic - AUS.docx"
            assert claim["source"]["section"]
            assert claim["source"]["excerpt"]


def test_committed_results_match_current_engine(tmp_path):
    generated_paths = generate_all(tmp_path)

    for generated_path in generated_paths:
        committed_path = (
            ROOT
            / "results"
            / generated_path.name
        )

        expected = json.loads(
            generated_path.read_text(encoding="utf-8")
        )

        actual = json.loads(
            committed_path.read_text(encoding="utf-8")
        )

        assert actual == expected
