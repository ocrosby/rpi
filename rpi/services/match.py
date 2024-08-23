"""
This module contains the MatchService class.
"""
import csv

from datetime import date, datetime, timedelta
from typing import Optional

import requests

from rpi.models.match import Match
from rpi.calculations import get_wins_for_team, get_losses_for_team, get_draws_for_team, wp, owp, oowp, rpi


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

    :param game:
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


def save_matches_to_csv(filename: str, matches: list[Match], state: Optional[str] = None):
    """
    Save the matches to a CSV file

    :param matches:
    :param filename:
    :return:
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header
        if state is None or state == "final":
            writer.writerow(
                ['home_team', 'away_team', 'home_score', 'away_score', 'start_date'])

            # Write the match data
            for match in matches:
                writer.writerow([
                    match.home_team,
                    match.away_team,
                    match.home_score,
                    match.away_score,
                    match.start_date
                ])

        elif state == "live":
            writer.writerow(['home_team', 'away_team', 'home_score', 'away_score', 'start_date', 'start_time'])

            # Write the match data
            for match in matches:
                writer.writerow([
                    match.home_team,
                    match.away_team,
                    match.home_score,
                    match.away_score,
                    match.start_date,
                    match.start_time
                ])
        elif state == "pre":
            writer.writerow(['home_team', 'away_team', 'start_date', 'start_time'])

            # Write the match data
            for match in matches:
                writer.writerow([
                    match.home_team,
                    match.away_team,
                    match.start_date,
                    match.start_time
                ])
        else:
            print(f"Invalid state: {state}")


def list_team_names(matches: list[Match]) -> list[str]:
    """
    List the team names from the matches

    :param matches:
    :return: List of team names
    """
    team_names_set = set()

    for match in matches:
        team_names_set.add(match.home_team)
        team_names_set.add(match.away_team)

    team_names_list = list(team_names_set)
    team_names_list.sort()

    return team_names_list


def calculate_statistics(matches: list[Match], ndigits: int = 2) -> dict:
    statistics = {}

    team_names = list_team_names(matches)
    for current_team_name in team_names:
        wp_value = wp(matches, current_team_name, None, ndigits)
        owp_value = owp(matches, current_team_name, ndigits)
        oowp_value = oowp(matches, current_team_name, ndigits)

        statistics[current_team_name] = {
            "wins": get_wins_for_team(matches, current_team_name, None),
            "losses": get_losses_for_team(matches, current_team_name, None),
            "draws": get_draws_for_team(matches, current_team_name, None),
            "wp": wp_value,
            "owp": owp_value,
            "oowp": oowp_value,
            "rpi": rpi(wp_value, owp_value, oowp_value, ndigits)
        }

    return statistics


def save_stats_to_csv(file_name: str, statistics: dict):
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['team', 'wins', 'losses', 'draws', 'wp', 'owp', 'oowp', 'rpi'])

        # Sort the statistics by the 'rpi' value in decending order and then by team name alphabetically
        sorted_statistics = sorted(statistics.items(), key=lambda item: (-item[1]['rpi'], item[0]))

        for current_team_name, current_team_statistics in sorted_statistics:
            writer.writerow([
                current_team_name,
                current_team_statistics["wins"],
                current_team_statistics["losses"],
                current_team_statistics["draws"],
                current_team_statistics["wp"],
                current_team_statistics["owp"],
                current_team_statistics["oowp"],
                current_team_statistics["rpi"]
            ])


if __name__ == "__main__":
    current_time = datetime.now()
    season_start_date = datetime(2024, 8, 15)

    completed_matches = get_matches_from(season_start_date, "final")
    live_matches = get_matches_on(current_time, "live")
    upcoming_matches = get_matches_on(current_time, "pre")

    save_matches_to_csv("completed_matches.csv", completed_matches, "final")
    save_matches_to_csv("live_matches.csv", live_matches, "live")
    save_matches_to_csv("upcoming_matches.csv", upcoming_matches, "pre")

    stats = calculate_statistics(completed_matches, 2)

    save_stats_to_csv("statistics.csv", stats)
