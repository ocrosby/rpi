"""
This module reads and exports matches from the NCAA given a gender, start date, and optional end date.
If the end date is not provided, the current date is used.
"""

import logging
import threading

from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from nis import match

import click
import requests

from tenacity import retry, stop_after_attempt, wait_fixed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print_lock = threading.Lock()

@click.group()
def cli():
    """
    Get matches from the NCAA given
    :return:
    """
    print("Todo: Implement this function")


def build_url(gender: str, division: str, date: datetime) -> str:
    """
    Build a URL to get matches from the NCAA

    :param gender: The gender to get matches for
    :param division: The division to get matches for
    :param date: The date to get matches for
    :return: The URL to get matches from the NCAA
    """
    if gender not in ["male", "female"]:
        raise ValueError(f"The specified gender '{gender}' is invalid! (expected male, or female)")

    if division not in ["d1", "d2", "d3"]:
        raise ValueError(f"The specified division '{division}' is invalid! (expected d1, d2, or d3)")

    gender_str = "soccer-men" if gender == "male" else "soccer-women"

    year_str = date.strftime("%Y")
    month_str = date.strftime("%m")
    day_str = date.strftime("%d")
    date_str = f"{year_str}/{month_str}/{day_str}"

    prefix = "https://data.ncaa.com/casablanca/scoreboard"
    url = f"{prefix}/{gender_str}/{division}/{date_str}/scoreboard.json"

    return url

def before_retry(retry_state):
    logger.info(f"Retrying {retry_state.fn.__name__} - Attempt {retry_state.attempt_number}")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_matches(gender: str, division: str, date: datetime) -> list[dict]:
    """
    Get matches from the NCAA given a date

    :param gender: The gender to get matches for
    :param division: The division to get matches for
    :param date: The date to get matches for
    :return: A list of matches
    """
    target_url = build_url(gender, division, date)

    with print_lock:
        logging.info(f"URL: {target_url}")

    response = requests.get(target_url)
    if response.status_code == 200:
        with print_lock:
            logging.info(f"Successfully got matches from '{target_url}' ...")
        data = response.json()

        games = data['games']

        matches = []
        for game in games:
            home = game['home']
            away = game['away']
            matches.append({
                'id': game['gameID'],
                'status': game['gameState'],
                'updated_time': int(datetime.strptime(game['updated_at'], '%m-%d-%Y %H:%M:%S').timestamp()),
                'start_time_epoch': game['startTimeEpoch'],
                'away': {
                    'name': away['names']['full'],
                    'score': away['score'],
                    'conference': away['conferences'][0]['conferenceName'],
                },
                'home': {
                    'name': home['names']['full'],
                    'score': home['score'],
                    'conference': home['conferences'][0]['conferenceName'],
                }
            })

        return matches
    elif response.status_code == 404:
        with print_lock:
            logging.error(f"No matches found for {target_url}")
        return []
    else:
        with print_lock:
            logging.error(f"Failed to get matches from {target_url} status code: {response.status_code}")
        return []


@cli.command()
@click.option('--gender', type=click.Choice(['male', 'female']), required=True, help='Gender can be male or female')
@click.option('--division', type=click.Choice(['d1', 'd2', 'd3']), required=True, help='Division can be d1, d2, or d3')
@click.option('--from-date', type=click.DateTime(formats=["%Y-%m-%d"]), required=True, help='Start date in YYYY-MM-DD format')
@click.option('--to-date', type=click.DateTime(formats=["%Y-%m-%d"]), default=datetime.today(), help='Optional end date in YYYY-MM-DD format, defaults to today')
def get(gender: str, division: str, from_date: datetime, to_date: datetime) -> list[dict]:
    """
    Get matches from the NCAA by gender and division.
    """
    print(f"Gender: {gender}")
    print(f"Division: {division}")
    print(f"From: {from_date}")
    print(f"To: {to_date}")

    matches = []

    current_date = from_date
    dates = []
    while current_date <= to_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda date: get_matches(gender, division, date), dates)
        for result in results:
            matches.extend(result)

    for match in matches:
        print(match)

if __name__ == "__main__":
    cli()
