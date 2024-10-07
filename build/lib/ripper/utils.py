"""
This module contains utility functions that are used in the project.
"""
import multiprocessing
import csv

from functools import partial
from datetime import datetime
from typing import Optional

from ripper.calculations import (
    get_draws_for_team,
    get_losses_for_team,
    get_wins_for_team,
    oowp,
    owp,
    rpi,
    wp,
)
from ripper.models.match import Match, Score, Team


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


def _get_field_names(status: str) -> list[str]:
    """
    Get the field names based on the status

    :param status: The status of the match
    :return: List of field names
    """
    if status in ["final", "live"]:
        fieldnames = [
            "gender",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "start_date",
            "start_time",
            "game_state",
            "home_conference",
            "away_conference",
        ]
    elif status == "pre":
        fieldnames = [
            "gender",
            "home_team",
            "away_team",
            "start_date",
            "start_time",
            "home_conference",
            "away_conference",
        ]
    else:
        raise ValueError(f"Invalid status: {status}")

    return fieldnames


class CSVStatisticsWriter:
    """
    Write a collection of statistics to a CSV file.
    """

    def __init__(self, filename: str):
        self.filename = filename
        self.fieldnames = ["team", "wins", "losses", "draws", "wp", "owp", "oowp", "rpi"]

    def write(self, stats: dict):
        sorted_stats = sort_stats(stats)

        with open(self.filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()

            for team_name, team_stats in sorted_stats:
                writer.writerow(
                    {
                        "team": team_name,
                        "wins": team_stats["wins"],
                        "losses": team_stats["losses"],
                        "draws": team_stats["draws"],
                        "wp": team_stats["wp"],
                        "owp": team_stats["owp"],
                        "oowp": team_stats["oowp"],
                        "rpi": team_stats["rpi"],
                    }
                )


class CSVMatchWriter:
    """
    Write a collection of matches to a CSV file.
    """

    def __init__(self, filename: str, status: Optional[str] = "final"):
        self.filename = filename
        self.status = status

    def write(self, matches: list[Match]):
        field_names = _get_field_names(self.status)
        with open(self.filename, "w") as file:
            writer = csv.DictWriter(file, fieldnames=field_names)
            writer.writeheader()

            for match in matches:
                if self.status in ["final", "live"]:
                    writer.writerow(
                        {
                            "gender": match.gender,
                            "home_team": match.home.name,
                            "away_team": match.away.name,
                            "home_score": match.score.home,
                            "away_score": match.score.away,
                            "start_date": match.date,
                            "start_time": match.time,
                            "game_state": match.status,
                            "home_conference": match.home.conference,
                            "away_conference": match.away.conference,
                        }
                    )
                elif self.status == "pre":
                    writer.writerow(
                        {
                            "gender": match.gender,
                            "home_team": match.home.name,
                            "away_team": match.away.name,
                            "start_date": match.date,
                            "start_time": match.time,
                            "home_conference": match.home.conference,
                            "away_conference": match.away.conference,
                        }
                    )
                else:
                    raise ValueError(f"Invalid status: {self.status}")


class CSVMatchReader:
    """
    Read a collection of matches from a CSV file.
    """

    def __init__(self, filename: str, status: Optional[str] = "final"):
        self.filename = filename
        self.status = status

    @staticmethod
    def read_row(row: dict[str, str]) -> Match:
        """
        Read a row from the CSV file and return a Match object.

        :param row:
        :return:
        """
        gender = row["gender"]
        home_team = Team(name=row["home_team"], conference=row["home_conference"])
        away_team = Team(name=row["away_team"], conference=row["away_conference"])
        score = Score(home=int(row["home_score"]), away=int(row["away_score"]))

        start_date = row["start_date"] if "start_date" in row else None
        start_time = row["start_time"] if "start_time" in row else None
        status = row["game_state"] if "game_state" in row else "final"


        new_match = Match(
            gender=gender,
            home=home_team,
            away=away_team,
            score=score,
            date=start_date,
            time=start_time,
            status=status,
        )

        return new_match

    def read(self) -> list[Match]:
        """
        Read all matches from the CSV file and return a list of Match objects.

        :return: list of Match objects
        """
        matches = []
        with open(self.filename, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                matches.append(CSVMatchReader.read_row(row))

        return matches

def list_team_names(matches: list[Match]) -> list[str]:
    """
    List the team names from the matches

    :param matches: The list of Match containing match data
    :return: List of team names
    """
    team_names_set = set()

    for match in matches:
        team_names_set.add(match.home.name)
        team_names_set.add(match.away.name)

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
    if filename is None:
        raise ValueError("Filename cannot be None")

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        if state is None or state in ["final", "live"]:
            fieldnames = [
                "gender",
                "home_team",
                "away_team",
                "home_score",
                "away_score",
                "start_date",
                "start_time",
                "home_conference",
                "away_conference"
            ]
        elif state == "pre":
            fieldnames = [
                "gender",
                "home_team",
                "away_team",
                "start_date",
                "start_time",
                "home_conference",
                "away_conference"
            ]
        else:
            print(f"Invalid state: {state}")
            return

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for match in matches:
            if state is None or state in ["final", "live"]:
                writer.writerow(
                    {
                        "gender": match.gender,
                        "home_team": match.home.name,
                        "away_team": match.away.name,
                        "home_score": match.score.home,
                        "away_score": match.score.away,
                        "start_date": match.date,
                        "start_time": match.time,
                        "home_conference": match.home.conference,
                        "away_conference": match.away.conference,
                    }
                )
            elif state == "pre":
                writer.writerow(
                    {
                        "gender": match.gender,
                        "home_team": match.home_team,
                        "away_team": match.away_team,
                        "start_date": match.date,
                        "start_time": match.time,
                        "home_conference": match.home.conference,
                        "away_conference": match.away.conference,
                    }
                )
            else:
                print(f"Invalid state: {state}")


def calculate_team_statistics(gender: str, matches: list[Match], team_name: str, precision: int) -> tuple[str, dict]:
    wp_value = wp(gender, matches, team_name, None, precision)
    owp_value = owp(gender, matches, team_name, precision)
    oowp_value = oowp(gender, matches, team_name, precision)

    statistics = {
        "wins": get_wins_for_team(gender, matches, team_name, None),
        "losses": get_losses_for_team(gender, matches, team_name, None),
        "draws": get_draws_for_team(gender, matches, team_name, None),
        "wp": wp_value,
        "owp": owp_value,
        "oowp": oowp_value,
        "rpi": rpi(wp_value, owp_value, oowp_value, precision),
    }

    return team_name, statistics

def calculate_statistics(gender: str, matches: list[Match], precision: int = 2) -> dict:
    """
    This function calculates statistics across matches

    :param matches: The list of matches containing match data
    :param precision: The number of decimal digits of precision
    :return:
    """
    print(f"Calculating statistics for {len(matches)} matches...")

    team_names = list_team_names(matches)
    num_workers = multiprocessing.cpu_count()

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(partial(calculate_team_statistics, gender, matches, precision=precision), team_names)

    return dict(results)


def find_root_dir():
    """
    Find the root directory of the project

    :return: The root directory of the project
    """
    import os

    return os.path.dirname(os.path.abspath(__file__))
