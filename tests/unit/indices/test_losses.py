import pytest

from ripper.indices.losses import LossesIndex
from ripper.models.match import Match


@pytest.fixture
def losses_index():
    return LossesIndex()


@pytest.fixture
def matches():
    return [
        Match(
            home_team="Team A", away_team="Team B", home_score=1, away_score=0
        ),  # Team B loss
        Match(
            home_team="Team B", away_team="Team C", home_score=2, away_score=1
        ),  # Team C loss
        Match(
            home_team="Team A", away_team="Team C", home_score=3, away_score=2
        ),  # Team C loss
        Match(
            home_team="Team C", away_team="Team A", home_score=0, away_score=1
        ),  # Team C loss
        Match(
            home_team="Team B", away_team="Team A", home_score=1, away_score=2
        ),  # Team B loss
        Match(
            home_team="Team A", away_team="Team B", home_score=2, away_score=1
        ),  # Team B loss
    ]


def test_empty_matches(losses_index):
    result = losses_index.calculate([])
    assert result == []


def test_single_match(losses_index):
    result = losses_index.calculate(
        [Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0)]
    )
    expected = [(1, "Team A", 0), (2, "Team B", 1)]
    assert result == expected


def test_multiple_matches(losses_index, matches):
    result = losses_index.calculate(matches)
    expected = [(1, "Team A", 0), (2, "Team B", 3), (3, "Team C", 3)]
    assert result == expected


def test_sorting_by_losses_and_name(losses_index):
    matches = [
        Match(
            home_team="Team B", away_team="Team A", home_score=1, away_score=2
        ),  # Team B loss
        Match(
            home_team="Team A", away_team="Team C", home_score=2, away_score=1
        ),  # Team C loss
        Match(
            home_team="Team B", away_team="Team C", home_score=1, away_score=0
        ),  # Team C loss
        Match(
            home_team="Team A", away_team="Team B", home_score=3, away_score=2
        ),  # Team B loss
        Match(
            home_team="Team C", away_team="Team A", home_score=0, away_score=1
        ),  # Team C loss
        Match(
            home_team="Team A", away_team="Team B", home_score=2, away_score=1
        ),  # Team B loss
    ]
    result = losses_index.calculate(matches)
    expected = [(1, "Team A", 0), (2, "Team B", 3), (3, "Team C", 3)]
    assert result == expected
