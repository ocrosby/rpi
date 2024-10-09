"""
This module contains utility functions that are used in the project.
"""

import csv
from datetime import datetime
from typing import Optional

from ripper.calculations import (get_draws_for_team, get_losses_for_team,
                                 get_wins_for_team, oowp, owp, rpi, wp)
from ripper.models.match import Match


def decompose_stats(stats: dict) -> list[tuple[str, dict]]:
    """
    Decompose the statistics into a list of tuples containing the team name and the statistics

    :param stats: The dictionary of statistics by team name.
    :return: List of tuples containing the team name and the statistics
    """
    return [(team_name, stats[team_name]) for team_name in stats]


def sort_stats(stats: dict) -> list[tuple[str, dict]]:
    """
    Sort the statistics by the 'RPI' value in descending order and then by team name alphabetically

    :param stats: The dictionary of statistics by team name.
    :return: List of tuples containing the team name and the statistics
    """
    return sorted(stats.items(), key=lambda item: (-item[1]["rpi"], item[0]))


def save_stats_to_csv(filename: str, stats_list: list[tuple[str, dict]]):
    """
    Save the statistics to a CSV file

    :param filename: The name of the CSV file to save the statistics to
    :param stats_list: List of tuples containing the team name and the statistics
    :return:
    """
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["team", "wins", "losses", "draws", "wp", "owp", "oowp", "rpi"])

        for current_team_name, current_team_statistics in stats_list:
            writer.writerow(
                [
                    current_team_name,
                    current_team_statistics["wins"],
                    current_team_statistics["losses"],
                    current_team_statistics["draws"],
                    current_team_statistics["wp"],
                    current_team_statistics["owp"],
                    current_team_statistics["oowp"],
                    current_team_statistics["rpi"],
                ]
            )


def list_team_names(matches: list[Match]) -> list[str]:
    """
    List the team names from the matches

    :param matches: The list of Match containing match data
    :return: List of team names
    """
    team_names_set = set()

    for match in matches:
        team_names_set.add(match.home_team)
        team_names_set.add(match.away_team)

    team_names_list = list(team_names_set)
    team_names_list.sort()

    return team_names_list


def get_start_date_and_time(utc_date_str: str) -> tuple[str, str]:
    # Parse the UTC date string
    dt = datetime.strptime(utc_date_str, "%Y-%m-%dT%H:%M:%SZ")

    # Extract and format the date and time
    start_date = dt.strftime("%Y-%m-%d")
    start_time = dt.strftime("%H:%M:%S")

    return start_date, start_time


def save_matches_to_csv(
    filename: str, matches: list[Match], state: Optional[str] = None
):
    """
    Save the matches to a CSV file

    :param filename: The file name to save matches to
    :param matches: The list of Match containing match data
    :param state: The optional state (live, pre, final)
    :return:
    """
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write the header
        if state is None or state == "final":
            writer.writerow(
                ["home_team", "away_team", "home_score", "away_score", "start_date"]
            )

            # Write the match data
            for match in matches:
                writer.writerow(
                    [
                        match.home_team,
                        match.away_team,
                        match.home_score,
                        match.away_score,
                        match.start_date,
                    ]
                )

        elif state == "live":
            writer.writerow(
                [
                    "home_team",
                    "away_team",
                    "home_score",
                    "away_score",
                    "start_date",
                    "start_time",
                ]
            )

            # Write the match data
            for match in matches:
                writer.writerow(
                    [
                        match.home_team,
                        match.away_team,
                        match.home_score,
                        match.away_score,
                        match.start_date,
                        match.start_time,
                    ]
                )
        elif state == "pre":
            writer.writerow(["home_team", "away_team", "start_date", "start_time"])

            # Write the match data
            for match in matches:
                writer.writerow(
                    [
                        match.home_team,
                        match.away_team,
                        match.start_date,
                        match.start_time,
                    ]
                )
        else:
            print(f"Invalid state: {state}")


def calculate_statistics(matches: list[Match], precision: int = 2) -> dict:
    """
    This function calculates statistics across matches

    :param matches: The list of matches containing match data
    :param precision: The number of decimal digits of precision
    :return:
    """
    statistics = {}

    team_names = list_team_names(matches)
    for current_team_name in team_names:
        wp_value = wp(matches, current_team_name, None, precision)
        owp_value = owp(matches, current_team_name, precision)
        oowp_value = oowp(matches, current_team_name, precision)

        statistics[current_team_name] = {
            "wins": get_wins_for_team(matches, current_team_name, None),
            "losses": get_losses_for_team(matches, current_team_name, None),
            "draws": get_draws_for_team(matches, current_team_name, None),
            "wp": wp_value,
            "owp": owp_value,
            "oowp": oowp_value,
            "rpi": rpi(wp_value, owp_value, oowp_value, precision),
        }

    return statistics


def find_root_dir():
    """
    Find the root directory of the project

    :return: The root directory of the project
    """
    import os

    return os.path.dirname(os.path.abspath(__file__))
