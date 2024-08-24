from ripper.constants import K_FACTOR, INITIAL_RATING
from ripper.models.match import Match

def initialize_ratings(teams: list[str]) -> dict[str, int]:
    """
    Initialize ratings for each team.

    :param teams: List of team names
    :return: Dictionary with team names as keys and their ratings as values
    """
    return {team: INITIAL_RATING for team in teams}

def expected_score(rating_a: int, rating_b: int) -> float:
    """
    Calculate the expected score for a match.

    :param rating_a: Rating of team A
    :param rating_b: Rating of team B
    :return: Expected score for team A
    """
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_ratings(rating_a: int, rating_b: int, score_a: float, score_b: float) -> tuple[int, int]:
    """
    Update the ratings based on the match result.

    :param rating_a: Rating of team A
    :param rating_b: Rating of team B
    :param score_a: Actual score of team A (1 for win, 0.5 for draw, 0 for loss)
    :param score_b: Actual score of team B (1 for win, 0.5 for draw, 0 for loss)
    :return: Updated ratings for team A and team B
    """
    expected_a = expected_score(rating_a, rating_b)
    expected_b = expected_score(rating_b, rating_a)

    new_rating_a = rating_a + K_FACTOR * (score_a - expected_a)
    new_rating_b = rating_b + K_FACTOR * (score_b - expected_b)

    return round(new_rating_a), round(new_rating_b)


def process_matches_with_elo(matches: list[Match]) -> dict[str, int]:
    """
    Process matches and calculate Elo ratings for each team.

    :param matches: List of matches
    :return: Dictionary with team names as keys and their final ratings as values
    """
    # Extract team names from matches
    teams = set()
    for match in matches:
        teams.add(match.home_team)
        teams.add(match.away_team)

    # Initialize ratings
    ratings = initialize_ratings(list(teams))

    # Process each match to update ratings
    for match in matches:
        if not match.is_finished():
            continue

        home_team = match.home_team
        away_team = match.away_team

        if match.is_draw():
            score_home = 0.5
            score_away = 0.5
        else:
            score_home = 1 if match.winner() == home_team else 0
            score_away = 1 if match.winner() == away_team else 0

        ratings[home_team], ratings[away_team] = update_ratings(
            ratings[home_team], ratings[away_team], score_home, score_away
        )

    return ratings
