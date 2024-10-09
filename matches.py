"""
This module reads and exports matches from the NCAA given a gender, start date, and optional end date.
If the end date is not provided, the current date is used.

This script was developed with Python 3.12

To utilize this you'll need to install the following dependencies:

pip install click
pip install requests
pip install tenacity

Running it:

> python3 matches.py get --gender female --division d1 --from-date 2024-08-15

This call will request all matches since the beginning of the season for women's soccer and save

female_d1_matches.csv
female_d1_team_conference_map.csv
female_d1_team_names.csv
"""

import csv
import logging
import os.path
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import click
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

BAD_URLS_LOG = "bad_urls.log"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print_lock = threading.Lock()


@click.group()
def cli():
    """
    Get matches from the NCAA given
    :return:
    """


def build_url(gender: str, division: str, date: datetime) -> str:
    """
    Build a URL to get matches from the NCAA

    :param gender: The gender to get matches for
    :param division: The division to get matches for
    :param date: The date to get matches for
    :return: The URL to get matches from the NCAA
    """
    if gender not in ["male", "female"]:
        raise ValueError(
            f"The specified gender '{gender}' is invalid! (expected male, or female)"
        )

    if division not in ["d1", "d2", "d3"]:
        raise ValueError(
            f"The specified division '{division}' is invalid! (expected d1, d2, or d3)"
        )

    gender_str = "soccer-men" if gender == "male" else "soccer-women"

    year_str = date.strftime("%Y")
    month_str = date.strftime("%m")
    day_str = date.strftime("%d")
    date_str = f"{year_str}/{month_str}/{day_str}"

    prefix = "https://data.ncaa.com/casablanca/scoreboard"
    url = f"{prefix}/{gender_str}/{division}/{date_str}/scoreboard.json"

    return url


def get_sorted_team_names(matches):
    team_names = set()  # Using a set to avoid duplicates

    for match in matches:
        team_names.add(match["away"]["name"])  # Add away team name
        team_names.add(match["home"]["name"])  # Add home team name

    # Return the sorted list of team names
    return sorted(team_names)


def map_teams_to_conference(matches):
    team_conference_map = {}

    for match in matches:
        # Map the away team to its conference only if not already mapped
        away_team = match["away"]["name"]
        away_conference = match["away"]["conference"]
        if away_team not in team_conference_map:
            team_conference_map[away_team] = away_conference

        # Map the home team to its conference only if not already mapped
        home_team = match["home"]["name"]
        home_conference = match["home"]["conference"]
        if home_team not in team_conference_map:
            team_conference_map[home_team] = home_conference

    return team_conference_map


def save_team_names_to_csv(team_names, filename):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Team Name"])  # Write the header
        for team in team_names:
            writer.writerow([team])  # Write each team name in a row


def epoch_to_human_readable(epoch: int) -> str:
    """
    Convert an epoch number to a human-readable date string.

    :param epoch: The epoch time in seconds
    :return: A human-readable date string in the format 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def save_matches_to_csv(sorted_matches, filename):
    with open(filename, mode="w", newline="") as file:
        fieldnames = [
            "id",
            "status",
            "updated_time",
            "start_time",
            "away_name",
            "away_score",
            "away_conference",
            "home_name",
            "home_score",
            "home_conference",
        ]

        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header

        # Write each match as a row
        for match in sorted_matches:
            updated_time = match["updated_time"]
            if isinstance(updated_time, int):
                updated_time = epoch_to_human_readable(updated_time)
            elif isinstance(updated_time, str):
                updated_time = int(updated_time)
                updated_time = epoch_to_human_readable(updated_time)

            start_time = match["start_time_epoch"]
            if isinstance(start_time, int):
                start_time = epoch_to_human_readable(start_time)
            elif isinstance(start_time, str):
                start_time = int(start_time)
                start_time = epoch_to_human_readable(start_time)

            writer.writerow(
                {
                    "id": match["id"],
                    "status": match["status"],
                    "updated_time": updated_time,
                    "start_time": start_time,
                    "away_name": match["away"]["name"],
                    "away_score": match["away"]["score"],
                    "away_conference": match["away"]["conference"],
                    "home_name": match["home"]["name"],
                    "home_score": match["home"]["score"],
                    "home_conference": match["home"]["conference"],
                }
            )


def save_team_conference_map_to_csv(team_conference_map, filename):
    with open(filename, mode="w", newline="") as file:
        fieldnames = ["Team Name", "Conference"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()  # Write the header

        # Sort the team names alphabetically and write each team and conference
        for team in sorted(team_conference_map):
            writer.writerow(
                {"Team Name": team, "Conference": team_conference_map[team]}
            )


def log_bad_url(url, filename=BAD_URLS_LOG):
    with open(filename, mode="a") as file:  # Open the file in append mode
        file.write(f"{url}\n")  # Write the URL followed by a newline


def before_retry(retry_state):
    logger.info(
        f"Retrying {retry_state.fn.__name__} - Attempt {retry_state.attempt_number}"
    )


# @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_matches(gender: str, division: str, date: datetime) -> list[dict]:
    """
    Get matches from the NCAA given a date

    :param gender: The gender to get matches for
    :param division: The division to get matches for
    :param date: The date to get matches for
    :return: A list of matches
    """
    target_url = build_url(gender, division, date)

    response = requests.get(target_url)
    if response.status_code == 200:
        data = response.json()

        games = data["games"]

        matches = []
        for game in games:
            inner_game = game["game"]
            home = inner_game["home"]
            away = inner_game["away"]
            status = inner_game["gameState"]

            if status == "pre":
                away_score = 0
                home_score = 0
            else:
                away_score = away["score"]
                home_score = home["score"]

                if isinstance(away_score, str):
                    if away_score == "":
                        away_score = 0
                    else:
                        away_score = int(away_score)

                if isinstance(home_score, str):
                    if home_score == "":
                        home_score = 0
                    else:
                        home_score = int(home_score)

            matches.append(
                {
                    "id": int(inner_game["gameID"]),
                    "status": inner_game["gameState"],
                    "updated_time": int(
                        datetime.strptime(
                            data["updated_at"], "%m-%d-%Y %H:%M:%S"
                        ).timestamp()
                    ),
                    "start_time_epoch": inner_game["startTimeEpoch"],
                    "away": {
                        "name": away["names"]["full"],
                        "score": away_score,
                        "conference": away["conferences"][0]["conferenceName"],
                    },
                    "home": {
                        "name": home["names"]["full"],
                        "score": home_score,
                        "conference": home["conferences"][0]["conferenceName"],
                    },
                }
            )

        return matches
    elif response.status_code == 404:
        with print_lock:
            log_bad_url(target_url)
        return []
    else:
        with print_lock:
            logging.error(
                f"Failed to get matches from {target_url} status code: {response.status_code}"
            )
        return []


@cli.command()
@click.option(
    "--gender",
    type=click.Choice(["male", "female"]),
    required=True,
    help="Gender can be male or female",
)
@click.option(
    "--division",
    type=click.Choice(["d1", "d2", "d3"]),
    required=True,
    help="Division can be d1, d2, or d3",
)
@click.option(
    "--from-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    required=True,
    help="Start date in YYYY-MM-DD format",
)
@click.option(
    "--to-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=datetime.today(),
    help="Optional end date in YYYY-MM-DD format, defaults to today",
)
def get(gender: str, division: str, from_date: datetime, to_date: datetime) -> None:
    """
    Get matches from the NCAA by gender and division.
    """
    if os.path.exists(BAD_URLS_LOG):
        os.remove(BAD_URLS_LOG)

    print(f"Gender: {gender}")
    print(f"Division: {division}")
    print(f"From: {from_date}")
    print(f"To: {to_date}")

    match_lock = threading.Lock()

    matches = []

    current_date = from_date
    dates = []
    while current_date <= to_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda date: get_matches(gender, division, date), dates)
        for result in results:
            with match_lock:
                matches.extend(result)

    # Sorting the matches by 'start_time_epoch'
    sorted_matches = sorted(matches, key=lambda x: int(x["start_time_epoch"]))

    team_names = get_sorted_team_names(sorted_matches)
    team_conference_map = map_teams_to_conference(sorted_matches)

    save_team_names_to_csv(team_names, f"{gender}_{division}_team_names.csv")
    save_matches_to_csv(sorted_matches, f"{gender}_{division}_matches.csv")
    save_team_conference_map_to_csv(
        team_conference_map, f"{gender}_{division}_team_conference_map.csv"
    )


if __name__ == "__main__":
    cli()
