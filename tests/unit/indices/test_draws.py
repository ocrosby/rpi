import pytest


from ripper.models.match import Match
from ripper.indices.draws import DrawsIndex

@pytest.fixture
def draws_index():
    return DrawsIndex()

def test_empty_matches(draws_index):
    result = draws_index.calculate([])

    assert result == []

def test_single_match_nondraw(draws_index):
    result = draws_index.calculate([Match(home_team="Team A", away_team="Team B", home_score=1, away_score=2)])
    expected = [
        (1, "Team A", 0),
        (2, "Team B", 0)
    ]
    assert result == expected

def test_single_match_draw(draws_index):
    result = draws_index.calculate([Match(home_team="Team A", away_team="Team B", home_score=1, away_score=1)])
    expected = [
        (1, "Team A", 1),
        (2, "Team B", 1)
    ]
    assert result == expected

def test_multiple_matches(draws_index):
    matches = [
        Match(home_team="Team A", away_team="Team B", home_score=1, away_score=1),
        Match(home_team="Team B", away_team="Team C", home_score=2, away_score=2),
        Match(home_team="Team A", away_team="Team C", home_score=3, away_score=3),
        Match(home_team="Team C", away_team="Team A", home_score=0, away_score=0),
        Match(home_team="Team B", away_team="Team A", home_score=1, away_score=1),
        Match(home_team="Team A", away_team="Team B", home_score=2, away_score=2)
    ]

    result = draws_index.calculate(matches)
    expected = [
        (1, "Team A", 5),
        (2, "Team B", 4),
        (3, "Team C", 3),
    ]
    assert result == expected
