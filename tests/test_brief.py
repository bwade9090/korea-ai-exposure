"""The brief's numbers: each placeholder resolves from its fact as recorded, and every placeholder
in the text names a fact in outputs/facts.json."""

import json

import pytest

from korea_ai_exposure import brief, paths

FACTS = {
    "share": {"value": 3.24, "display": "3.24%"},
    "rank": {"value": 7, "display": "7 of 121"},
    "rho": {"value": -0.381, "display": "-0.38 (N = 17)"},
    "gap": {"value": -2.181639, "display": "Sales: -2.18 pp"},
    "share.seoul": {"value": 63.65, "display": "63.65%"},
}


def test_placeholders_resolve_from_the_facts():
    text = "{share} {rank!ordw}, of {rank!total}; {rho!num}; {gap!abs:.1f}; {share:.1f}"
    expected = f"3.24% seventh, of 121; {brief.MINUS}0.38; 2.2; 3.2"
    assert brief.resolve(text, FACTS) == expected
    assert brief.resolve("{share.seoul} (N = 17)", FACTS) == "63.65% (N = 17)"


def test_an_unknown_fact_or_conversion_is_an_error():
    with pytest.raises(KeyError):
        brief.resolve("{missing}", FACTS)
    with pytest.raises(ValueError):
        brief.resolve("{rank!word}", FACTS)


@pytest.mark.data("outputs/facts.json")
def test_every_placeholder_in_the_brief_names_a_fact():
    facts = {fact["id"]: fact for fact in json.loads((paths.OUTPUTS / "facts.json").read_text())}
    for text in brief.texts():
        assert "{" not in brief.resolve(text, facts), text
