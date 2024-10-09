import pytest

from ripper.indices.matches_played import MatchesPlayedIndex
from ripper.models.match import Match


@pytest.fixture
def matches_played_index():
    return MatchesPlayedIndex()


def test_empty_matches(matches_played_index):
    result = matches_played_index.calculate([])
    assert result == []


def test_single_match(matches_played_index):
    result = matches_played_index.calculate(
        [Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0)]
    )
    expected = [(1, "Team A", 1), (2, "Team B", 1)]
    assert result == expected


def test_multiple_matches(matches_played_index):
    matches = [
        Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0),
        Match(home_team="Team B", away_team="Team C", home_score=2, away_score=1),
        Match(home_team="Team A", away_team="Team C", home_score=3, away_score=2),
        Match(home_team="Team C", away_team="Team A", home_score=0, away_score=1),
        Match(home_team="Team B", away_team="Team A", home_score=1, away_score=2),
        Match(home_team="Team A", away_team="Team B", home_score=2, away_score=1),
    ]
    result = matches_played_index.calculate(matches)
    expected = [(1, "Team A", 5), (2, "Team B", 4), (3, "Team C", 3)]
    assert result == expected
