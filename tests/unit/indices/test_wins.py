import pytest
from ripper.models.match import Match
from ripper.indices.wins import WinsIndex

@pytest.fixture
def wins_index():
    return WinsIndex()

@pytest.fixture
def matches():
    return [
        Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0),
        Match(home_team="Team B", away_team="Team C", home_score=2, away_score=1),
        Match(home_team="Team A", away_team="Team C", home_score=3, away_score=2),
        Match(home_team="Team C", away_team="Team A", home_score=0, away_score=1),
        Match(home_team="Team B", away_team="Team A", home_score=1, away_score=2),
        Match(home_team="Team A", away_team="Team B", home_score=2, away_score=1)
    ]

def test_empty_matches(wins_index):
    result = wins_index.calculate([])
    assert result == []

def test_single_match(wins_index):
    result = wins_index.calculate([Match(home_team="Team A", away_team="Team B", home_score=1, away_score=0)])
    expected = [
        (1, "Team A", 1),
        (2, "Team B", 0)
    ]
    assert result == expected

def test_multiple_matches(wins_index, matches):
    result = wins_index.calculate(matches)
    expected = [
        (1, "Team A", 5),
        (2, "Team B", 1),
        (3, "Team C", 0)
    ]
    assert result == expected

def test_sorting_by_wins_and_name(wins_index):
    matches = [
        Match(home_team="Team B", away_team="Team A", home_score=1, away_score=2),
        Match(home_team="Team A", away_team="Team C", home_score=2, away_score=1),
        Match(home_team="Team B", away_team="Team C", home_score=1, away_score=0),
        Match(home_team="Team A", away_team="Team B", home_score=3, away_score=2),
        Match(home_team="Team C", away_team="Team A", home_score=0, away_score=1),
        Match(home_team="Team A", away_team="Team B", home_score=2, away_score=1)
    ]
    result = wins_index.calculate(matches)
    expected = [
        (1, "Team A", 5),
        (2, "Team B", 1),
        (3, "Team C", 0)
    ]
    assert result == expected
