"""
This module contains the MatchService class.
"""
from datetime import datetime, timedelta
from typing import Optional

import requests

from ripper.utils import save_matches_to_csv, save_stats_to_csv, calculate_statistics, sort_stats
from ripper.models.match import Match

SEASON_START_DATE = datetime(2024, 8, 14)

def generate_url(target_date: datetime) -> str:
    """
    Generate a URL for the specified date

    :param target_date:
    :return:
    """
    year = target_date.year
    month = target_date.month
    day = target_date.day

    return f"https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/{year}/{month:02}/{day:02}/scoreboard.json"


def generate_date_tuples(year: int, month: int, day: int) -> list[tuple]:
    """
    Generate date tuples from the specified year, month, and day to the current date

    :param year:
    :param month:
    :param day:
    :return:
    """
    from_date = datetime(year, month, day)
    date_tuples = []
    current_date = datetime.now()

    while from_date <= current_date:
        date_tuples.append((from_date.year, from_date.month, from_date.day))
        from_date += timedelta(days=1)

    return date_tuples


def get_match_from_game(game: dict) -> Match:
    """
    Get a match from a game dictionary

    :param game: Game dictionary
    :return:
    """
    game = game.get('game')
    home = game.get("home")
    away = game.get("away")

    return Match(
        home_team=home.get("names")["full"],
        away_team=away.get("names")["full"],
        home_score=home.get("score", 0),
        away_score=away.get("score", 0),
        start_date=game.get("startDate", None),
        start_time=game.get("startTime", None),
        game_state=game.get("gameState", None)
    )


def get_matches_on(target_date: datetime, state: Optional[str] = None) -> list[Match]:
    """
    Get matches from the specified start_date of the specified state

    :param target_date: Target date
    :param state: Optional state
    :return:
    """
    # Generate a URL for the specified date
    url = generate_url(target_date)
    response = requests.get(url)
    json_data = response.json()

    response_matches = []

    for game in json_data.get("games", []):
        current_match = get_match_from_game(game)

        if state is None or current_match.game_state == state:
            response_matches.append(current_match)

    return response_matches


def get_matches_from(from_date: datetime, state: Optional[str] = None) -> list[Match]:
    """
    Get matches from the specified from_date to the current date

    :param from_date: From date
    :param state: Optional state
    :return:
    """
    date_tuples = generate_date_tuples(from_date.year, from_date.month, from_date.day)
    response_matches = []

    for date_tuple in date_tuples:
        response_matches.extend(get_matches_on(datetime(*date_tuple), state))

    return response_matches


if __name__ == "__main__":
    current_time = datetime.now()
    season_start_date = datetime(2024, 8, 1)

    completed_matches = get_matches_from(season_start_date, "final")
    live_matches = get_matches_on(current_time, "live")
    upcoming_matches = get_matches_on(current_time, "pre")

    save_matches_to_csv("completed_matches.csv", completed_matches, "final")
    save_matches_to_csv("live_matches.csv", live_matches, "live")
    save_matches_to_csv("upcoming_matches.csv", upcoming_matches, "pre")

    stats = sort_stats(calculate_statistics(completed_matches, 2))
    save_stats_to_csv("statistics.csv", stats)
