"""
This module contains the MatchService class.
"""

import csv
import time
import threading
import concurrent.futures

from datetime import datetime, timedelta, date
from typing import Optional

import requests

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ripper.models.scoreboard import RootModel, Game, GameWrapper
from ripper.models.match import Match, Team, Score, CrossDivisionMatchException
from ripper.tools.date import DateUntilCurrentIterator
from ripper.utils import (
    calculate_statistics,
    save_matches_to_csv,
    save_stats_to_csv,
    sort_stats,
    CSVMatchReader,
    CSVMatchWriter,
)
from utils import CSVStatisticsWriter

SEASON_START_DATE = datetime(2024, 8, 14)

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(requests.exceptions.RequestException)
)
def get_ncaa_school_names_by_division(division: str) -> list[str]:
    """
    Get NCAA school names by division

    :param division: Division
    :return:
    """
    host = "web3.ncaa.org"
    resource = "/directory/api/directory/memberList?type=12&division="
    prefix = f"https://{host}{resource}"
    url_map = {
        "DI": f"{prefix}I",
        "DII": f"{prefix}II",
        "DIII": f"{prefix}III",
    }

    print(f"Fetching school names by division from {url_map[division]}")

    if division is None:
        raise ValueError("Division cannot be None")

    division = division.strip()

    if division == "":
        raise ValueError("Division cannot be empty")

    division = division.upper()

    if division not in url_map:
        raise ValueError(f"Invalid division: {division}")

    url = url_map[division]
    response = requests.get(url, timeout=5)
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

    prefix = "https://data.ncaa.com/casablanca/scoreboard/soccer-women"
    if division == "DI":
        return f"{prefix}/d1/{year}/{month:02}/{day:02}/scoreboard.json"

    if division == "DII":
        return f"{prefix}/d2/{year}/{month:02}/{day:02}/scoreboard.json"

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
    home_conference = home.get("conferences")[0].get("conferenceName")
    away_conference = away.get("conferences")[0].get("conferenceName")

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
        home_conference=home_conference,
        away_conference=away_conference,
    )


class ScoreboardDataRetriever:
    def __init__(self, gender: str, division: str, date_obj: date):
        gender = gender.strip()
        division = division.strip()

        if len(gender) == 0:
            raise ValueError("The gender cannot be empty")

        if len(division) == 0:
            raise ValueError("The division cannot be empty")

        # Convert gender to lowercase
        gender = gender.lower()

        # Convert division to lowercase
        division = division.lower()

        if gender not in ["men", "women", "male", "female"]:
            raise ValueError(f"Invalid gender value provided: {gender}")

        if division not in ["d1", "d2", "d3"]:
            raise ValueError(f"Invalid division value provided: {division} expected d1, d2, or d3")

        self.gender = gender
        self.division = division
        self.date_obj = date_obj

    def build_url(self) -> str:
        # G: https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/2024/09/01/scoreboard.json
        # B: https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/2024/08/01/scoreboard.json
        prefix = "https://data.ncaa.com/casablanca/scoreboard/soccer"

        if self.gender in ["male", "men"]:
            return f"{prefix}-men/{self.division}/{self.date_obj.strftime('%Y/%m/%d')}/scoreboard.json"
        elif self.gender in ["female", "women"]:
            return f"{prefix}-women/{self.division}/{self.date_obj.strftime('%Y/%m/%d')}/scoreboard.json"
        else:
            raise ValueError(f"Invalid gender value provided {self.gender}")



    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=30),
        retry=(
                retry_if_exception_type(requests.exceptions.HTTPError) |
                retry_if_exception_type(requests.exceptions.Timeout) |
                retry_if_exception_type(requests.exceptions.ConnectionError) |
                retry_if_exception_type(requests.exceptions.RequestException))
    )
    def fetch(self) -> Optional[RootModel]:
        url = self.build_url()

        headers = {
            "User-Agent": "CustomUserAgent/1.0",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 404:
                print(f"Data not found for this URL '{url}'!")
                return None

            response.raise_for_status()  # Raise an HTTPError for other bad responses (4xx and 5xx)
            root_model = RootModel.model_validate(
                response.json()  # Parse the JSON data
            )  # Parse the JSON data into a RootModel object
            return root_model
        except requests.exceptions.HTTPError as http_err:
            print(f"Something went wrong check this URL '{url}'!")
            print(f"HTTP error occurred: {http_err}")
            raise
        except ValueError as json_err:
            print(f"JSON decoding error: {json_err}")
            raise


def translate_game_wrapper_to_match(game_wrapper: GameWrapper) -> Match:
    """
    Translate a GameWrapper object to a Match object

    :param game_wrapper: GameWrapper object
    :return:
    """
    game = game_wrapper.game

    if is_match_cross_division(game.home.names.full, game.away.names.full):
        raise CrossDivisionMatchException(game.home.names.full,
                                          game.away.names.full,
                                          game.home.conferences[0].conferenceName,
                                          game.away.conferences[0].conferenceName)

    return Match(
        home=Team(name=game.home.names.full, conference=game.home.conferences[0].conferenceName),
        away=Team(name=game.away.names.full, conference=game.away.conferences[0].conferenceName),
        score=Score(home=game.home.score, away=game.away.score),
        date=game.startDate,
        time=game.startTime,
        status=game.gameState,
    )

def get_matches_on(
    gender: str, target_datetime: datetime, status: Optional[str] = None, division: Optional[str] = "d1"
) -> list[Match]:
    """
    Get matches from the specified start_date of the specified state

    :param target_datetime: Target date
    :param status: Optional state
    :return:
    """
    target_date = target_datetime.date()

    cumulative_matches = []

    # Handle women's data
    women_retriever = ScoreboardDataRetriever(gender=gender, division=division, date_obj=target_date)

    try:
        women_root_model = women_retriever.fetch()

        if women_root_model is not None:
            for game in women_root_model.games:
                try:
                    current_match = translate_game_wrapper_to_match(game)
                    current_match.gender = "female"

                    if current_match is None:
                        continue

                    if status is None or current_match.status == status:
                        cumulative_matches.append(current_match)
                except ValueError as err:
                    print(f"Failed to translate women's game {err}")
                except CrossDivisionMatchException as err:
                    # Do not add cross-division matches
                    continue
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
            ValueError) as err:
        print(f"Failed to fetch women's data: {err}")
        return []

    # Handle men's data
    men_retriever = ScoreboardDataRetriever(gender='men', division=division, date_obj=target_date)

    try:
        men_root_model = men_retriever.fetch()

        if men_root_model is not None:
            for game in men_root_model.games:
                try:
                    current_match = translate_game_wrapper_to_match(game)
                    current_match.gender = "male"

                    if current_match is None:
                        continue

                    if status is None or current_match.status == status:
                        cumulative_matches.append(current_match)
                except ValueError as err:
                    print(f"Failed to translate men's game {err}")
                except CrossDivisionMatchException as err:
                    # Do not add cross-division matches
                    continue
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
            ValueError) as err:
        print(f"Failed to fetch men's data: {err}")


    return cumulative_matches


def get_matches_from(
    gender: str, from_date: datetime, state: Optional[str] = None, division: Optional[str] = "d1"
) -> list[Match]:
    """
    Get matches from the specified from_date to the current date

    :param from_date: From date
    :param state: Optional state
    :return:
    """
    date_tuples = [datetime(*date_tuple) for date_tuple in DateUntilCurrentIterator(from_date)]
    cumulative_matches = []
    lock = threading.Lock()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_date = {executor.submit(get_matches_on, gender, date, state, division): date for date in date_tuples}

        for future in concurrent.futures.as_completed(future_to_date):
            try:
                current_matches = future.result()
                if current_matches:
                    with lock:
                        cumulative_matches.extend(current_matches)
            except Exception as exc:
                print(f"An error occurred: {exc}")

    return cumulative_matches


def list_conference_names(matches: list[Match]) -> list[str]:
    """
    List the unique conference names from the matches

    :param matches: The list of Match containing match data
    :return: List of unique conference names
    """
    conference_names_set = set()

    for match in matches:
        conference_names_set.add(match.home.conference)
        conference_names_set.add(match.away.conference)

    conference_names_list = list(conference_names_set)
    conference_names_list.sort()

    return conference_names_list

def map_team_to_conference(team_name: str, conference_name: str, mapping: dict[str, str]) -> None:
    """
    Map a team to a conference

    :param team_name: The name of the team
    :param conference_name: The name of the conference
    :param mapping: The mapping of team name to conference name
    :return: None
    """
    if team_name in mapping:
        return

    mapping[team_name] = conference_name


def map_teams_to_conferences(matches: list[Match]) -> dict[str, str]:
    # Determine a team to conference mapping
    team_to_conference_mapping = {}

    for match in matches:
        map_team_to_conference(match.home.name, match.home.conference, team_to_conference_mapping)
        map_team_to_conference(match.away.name, match.away.conference, team_to_conference_mapping)

    return team_to_conference_mapping

def format_conference_name(conference: str) -> str:
    """
    Convert a conference name to lowercase and replace spaces with underscores.

    :param conference: The conference name
    :return: The formatted conference name
    """
    return conference.lower().replace(" ", "_")

def list_teams_in_conference(matches: list[Match], target_conference: str) -> list[str]:
    """
    List the teams in a conference

    :param matches: The list of Match containing match data
    :param conference: The name of the conference
    :return: The list of teams in the conference
    """

    team_set = set()
    for match in matches:
        if match.home.conference == target_conference:
            team_set.add(match.home.name)

        if match.away.conference == target_conference:
            team_set.add(match.away.name)

    team_list = list(team_set)
    team_list.sort()

    return team_list

def generate_conference_rpi_mapping(matches: list[Match], stats: dict[str, dict[str, float]]) -> dict[str, float]:
    """
    Generate a mapping of conference to RPI

    :param matches: The list of Match containing match data
    :param stats: The dictionary of team statistics
    :return: The mapping of conference to RPI
    """
    conference_names = list_conference_names(matches)
    team_to_conference_mapping = map_teams_to_conferences(matches)

    # For each conference determine the average RPI of the teams in the conference
    conference_rpi = {}

    # Given the stats determine the average RPI of the teams in the conference
    for conference_name in conference_names:
        conference_team_names = list_teams_in_conference(matches, conference_name)

        sum_so_far = float(0)
        count = 0
        for conference_team_name in conference_team_names:
            conference_team_stats = stats.get(conference_team_name)
            if conference_team_stats is None:
                print(f"Statistics not found for {conference_team_name}")
                continue

            conference_team_rpi = conference_team_stats.get("rpi")
            if conference_team_rpi is None:
                print(f"RPI not found for {conference_team_name}")
                continue

            count += 1
            sum_so_far += conference_team_rpi

        if count == 0:
            conference_rpi_average = float(0)
        else:
            conference_rpi_average = sum_so_far / float(count)

        conference_rpi[conference_name] = conference_rpi_average

    conference_rpi = dict(sorted(conference_rpi.items(), key=lambda item: item[1], reverse=True))

    return conference_rpi

def process(gender: str):
    current_time = datetime.now()
    season_start_date = datetime(2024, 8, 15)

    start_time = time.time()
    completed_matches = get_matches_from(gender, season_start_date, "final")
    elapsed_time = time.time() - start_time
    print(f"Elapsed time for completed match retrieval: {elapsed_time:.2f} seconds")
    print(f"Number of completed matches: {len(completed_matches)}")

    start_time = time.time()
    live_matches = get_matches_on(gender, current_time, "live")
    elapsed_time = time.time() - start_time
    print(f"Elapsed time for live match retrieval: {elapsed_time:.2f} seconds")
    print(f"Number of live matches: {len(live_matches)}")

    start_time = time.time()
    upcoming_matches = get_matches_on(gender, current_time, "pre")
    elapsed_time = time.time() - start_time
    print(f"Elapsed time for upcoming match retrieval: {elapsed_time:.2f} seconds")
    print(f"Number of upcoming matches: {len(upcoming_matches)}")

    CSVMatchWriter("completed_matches.csv", "final").write(completed_matches)
    CSVMatchWriter("live_matches.csv", "live").write(live_matches)
    CSVMatchWriter("upcoming_matches.csv", "pre").write(upcoming_matches)

    print(f"Calculate {gender} Statistics")
    start_time = time.time()
    stats = calculate_statistics(gender, completed_matches, 2)
    elapsed_time = time.time() - start_time
    print(f"Elapsed time for {gender} statistics calculation: {elapsed_time:.2f} seconds")
    CSVStatisticsWriter(f"{gender}_statistics.csv").write(stats)

    conference_names = list_conference_names(completed_matches)
    team_to_conference_mapping = map_teams_to_conferences(completed_matches)
    conference_rpi = generate_conference_rpi_mapping(completed_matches, stats)
    generate_gender_conference_rpi_csv_file(gender, conference_rpi)
    generate_conference_teams_rpi_csv_files(gender, conference_names, stats, team_to_conference_mapping)


def generate_conference_teams_rpi_csv_files(gender, conference_names, stats, team_to_conference_mapping):
    for conference in conference_names:
        generate_conference_teams_rpi_csv_file(gender, conference, stats, team_to_conference_mapping)


def generate_gender_conference_rpi_csv_file(gender, conference_rpi_mapping):
    with open(f"{gender}_conference_rpi.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=["rank", "conference", "average_rpi"])
        writer.writeheader()
        rank = 1
        for conference in conference_rpi_mapping:
            average_rpi = round(conference_rpi_mapping[conference], 2)
            writer.writerow({"rank": rank, "conference": conference, "average_rpi": average_rpi})
            rank += 1


def generate_conference_teams_rpi_csv_file(gender, conference_name, stats, team_to_conference_mapping):
    conference_teams = [team for team in stats if team_to_conference_mapping[team] == conference_name]
    conference_rpi = {team: stats[team]["rpi"] for team in conference_teams}
    sorted_teams = sorted(conference_rpi.items(), key=lambda item: item[1], reverse=True)
    sorted_teams_rpi = dict(sorted_teams)
    formatted_conference_name = format_conference_name(conference_name)

    with open(f"{gender}_{formatted_conference_name}_rpi.csv", "w") as file:
        writer = csv.DictWriter(file, fieldnames=["rank", "team", "rpi"])
        writer.writeheader()
        rank = 1
        for team in sorted_teams_rpi:
            writer.writerow({"rank": rank, "team": team, "rpi": sorted_teams_rpi[team]})
            rank += 1


if __name__ == "__main__":
    process("male")
    process("female")
