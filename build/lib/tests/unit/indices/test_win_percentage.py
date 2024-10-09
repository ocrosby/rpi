import pytest

from ripper.indices.win_percentage import WinPercentageIndex
from ripper.models.match import Match


@pytest.fixture
def win_percentage_index():
    return WinPercentageIndex()


def test_empty_matches(win_percentage_index):
    result = win_percentage_index.calculate([])

    assert result == []


def test_single_match(win_percentage_index):
    result = win_percentage_index.calculate(
        [Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0)]
    )
    expected = [(1, "Team A", 1.0), (2, "Team B", 0.0)]
    assert result == expected


def test_multiple_matches(win_percentage_index):
    matches = [
        Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0),
        Match(home_team="Team B", away_team="Team C", home_score=2, away_score=1),
        Match(home_team="Team A", away_team="Team C", home_score=3, away_score=2),
        Match(home_team="Team C", away_team="Team A", home_score=0, away_score=1),
        Match(home_team="Team B", away_team="Team A", home_score=1, away_score=2),
        Match(home_team="Team A", away_team="Team B", home_score=2, away_score=1),
    ]

    # Team A has 5 wins and 0 losses with a total of 5 matches
    # Team B has 1 win and 3 losses with a total of 4 matches
    # Team C has 0 wins and 3 losses with a total of 3 matches

    result = win_percentage_index.calculate(matches)
    expected = [(1, "Team A", 1.0), (2, "Team B", 0.25), (3, "Team C", 0.0)]
    assert result == expected
