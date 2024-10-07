"""
This module contains the MatchService class.
"""

from datetime import datetime, timedelta
from typing import Optional

import requests

from ripper.utils import (
    save_matches_to_csv,
    save_stats_to_csv,
    calculate_statistics,
    sort_stats,
)
from ripper.models.match import Match

SEASON_START_DATE = datetime(2024, 8, 14)


def get_ncaa_school_names_by_division(division: str) -> list[str]:
    """
    Get NCAA school names by division

    :param division: Division
    :return:
    """
    # url = f"https://data.ncaa.com/casablanca/scoreboard/soccer-w"

    url_map = {
        "DI": "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=I",
        "DII": "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=II",
        "DIII": "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=III",
    }

    if division is None:
        raise ValueError("Division cannot be None")

    division = division.strip()

    if division == "":
        raise ValueError("Division cannot be empty")

    division = division.upper()

    if not division in url_map.keys():
        raise ValueError(f"Invalid division: {division}")

    url = url_map[division]
    response = requests.get(url)
    data = response.json()
    school_names = [school.get("nameOfficial") for school in data]
    sorted_school_names = sorted(school_names)

    return sorted_school_names


def map_ncaa_schools_by_division() -> dict[str, str]:
    """
    Map NCAA schools by division

    :return:
    """
    division_priority = ["DI", "DII", "DIII"]
    mapping = {}

    for division in division_priority:
        schools = get_ncaa_school_names_by_division(division)
        for school in schools:
            if school not in mapping:
                mapping[school] = division

    return mapping


def generate_url(target_date: datetime, division: Optional[str] = "DI") -> str:
    """
    Generate a URL for the specified date

    :param target_date:
    :return:
    """
    year = target_date.year
    month = target_date.month
    day = target_date.day

    if division == "DI":
        return f"https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/{year}/{month:02}/{day:02}/scoreboard.json"
    elif division == "DII":
        return f"https://data.ncaa.com/casablanca/scoreboard/soccer-women/d2/{year}/{month:02}/{day:02}/scoreboard.json"
    else:
        raise ValueError(f"Invalid division: {division}")


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


school_name_to_division = map_ncaa_schools_by_division()


def is_match_cross_division(home_team: str, away_team: str) -> bool:
    """
    Check if a match is cross-division

    :param home_team: Home team
    :param away_team: Away team
    :return:
    """
    home_division = school_name_to_division.get(home_team)
    away_division = school_name_to_division.get(away_team)

    if home_division is None:
        home_division = "Other"

    if away_division is None:
        away_division = "Other"

    answer = home_division != away_division

    if answer:
        print(
            f"Detected Cross-division match: {home_team} ({home_division}) vs {away_team} ({away_division})"
        )

    return answer


def get_match_from_game(game: dict) -> Optional[Match]:
    """
    Get a match from a game dictionary

    :param game: Game dictionary
    :return:
    """
    game = game.get("game")
    home = game.get("home")
    away = game.get("away")

    home_team_name = home.get("names")["full"]
    away_team_name = away.get("names")["full"]

    if is_match_cross_division(home_team_name, away_team_name):
        return None

    return Match(
        home_team=home_team_name,
        away_team=away_team_name,
        home_score=home.get("score", 0),
        away_score=away.get("score", 0),
        start_date=game.get("startDate", None),
        start_time=game.get("startTime", None),
        game_state=game.get("gameState", None),
    )


def get_matches_on(
    target_date: datetime, state: Optional[str] = None, division: Optional[str] = "DI"
) -> list[Match]:
    """
    Get matches from the specified start_date of the specified state

    :param target_date: Target date
    :param state: Optional state
    :return:
    """
    # Generate a URL for the specified date
    url = generate_url(target_date, division)
    response = requests.get(url)

    if response.status_code != 200:
        return []

    json_data = response.json()

    response_matches = []

    for game in json_data.get("games", []):
        current_match = get_match_from_game(game)

        if current_match is None:
            continue

        if state is None or current_match.game_state == state:
            response_matches.append(current_match)

    return response_matches


def get_matches_from(
    from_date: datetime, state: Optional[str] = None, division: Optional[str] = "DI"
) -> list[Match]:
    """
    Get matches from the specified from_date to the current date

    :param from_date: From date
    :param state: Optional state
    :return:
    """
    date_tuples = generate_date_tuples(from_date.year, from_date.month, from_date.day)
    response_matches = []

    for date_tuple in date_tuples:
        response_matches.extend(get_matches_on(datetime(*date_tuple), state, division))

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
