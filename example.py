import datetime

<<<<<<< HEAD
from dataclasses import dataclass

=======
>>>>>>> 000d4ad (chore: wip)
import requests

START_DATE = "2024/08/15"

<<<<<<< HEAD
@dataclass
class Match:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    start_date: str
    start_time: str
    game_state: str

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.home_score} - {self.away_score} - {self.start_date} - {self.start_time} - '{self.game_state}'"

    def is_live(self):
        return self.game_state == "live"

    def is_finished(self):
        return self.game_state == "final"

    def is_upcoming(self):
        return self.game_state == "pre"


def generate_url(year: int, month: int, day: int) -> str:
    return f"https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/{year}/{month:02}/{day:02}/scoreboard.json"


def get_finished_matches(url: str) -> list[Match]:
    response = requests.get(url)
    games = response.json().get("games", [])

    current_matches = []
    for game in games:
        game = game.get('game')
        home = game.get("home")
        away = game.get("away")

        current_match = Match(
            home_team = home.get("names")["full"],
            away_team = away.get("names")["full"],
            home_score = home.get("score", 0),
            away_score = away.get("score", 0),
            start_date = game.get("startDate", None),
            start_time = game.get("startTime", None),
            game_state = game.get("gameState", None)
        )

        if not current_match.is_finished():
            continue

        current_matches.append(current_match)

    return current_matches


def get_live_matches() -> list[Match]:
    now = datetime.datetime.now()
    url = generate_url(now.year, now.month, now.day)
    response = requests.get(url)
    games = response.json().get("games", [])

    current_matches = []
    for game in games:
        game = game.get('game')
        home = game.get("home")
        away = game.get("away")

        current_match = Match(
            home_team = home.get("names")["full"],
            away_team = away.get("names")["full"],
            home_score = home.get("score", 0),
            away_score = away.get("score", 0),
            start_date = game.get("startDate", None),
            start_time = game.get("startTime", None),
            game_state = game.get("gameState", None)
        )

        if not current_match.is_live():
            continue

        current_matches.append(current_match)

    return current_matches


def get_upcoming_matches() -> list[Match]:
    now = datetime.datetime.now()
    url = generate_url(now.year, now.month, now.day)
    response = requests.get(url)
    games = response.json().get("games", [])

    current_matches = []
    for game in games:
        game = game.get('game')
        home = game.get("home")
        away = game.get("away")

        current_match = Match(
            home_team = home.get("names")["full"],
            away_team = away.get("names")["full"],
            home_score = home.get("score", 0),
            away_score = away.get("score", 0),
            start_date = game.get("startDate", None),
            start_time = game.get("startTime", None),
            game_state = game.get("gameState", None)
        )

        if not current_match.is_upcoming():
            continue

        current_matches.append(current_match)

    return current_matches


def generate_date_tuples(year: int, month: int, day: int) -> list[tuple]:
    from_date = datetime.datetime(year, month, day)
    date_tuples = []
    current_date = datetime.datetime.now()

    while from_date <= current_date:
        date_tuples.append((from_date.year, from_date.month, from_date.day))
        from_date += datetime.timedelta(days=1)

    return date_tuples


def get_matches_since(year: int, month: int, day: int) -> list[Match]:
    date_tuples = generate_date_tuples(year, month, day)

    matches_since = []
    for date_tuple in date_tuples:
        url = generate_url(*date_tuple)
        current_scores = get_finished_matches(url)
        matches_since.extend(current_scores)

    return matches_since


if __name__ == '__main__':
    print("Matches since 2024/08/15")
    for match in get_matches_since(2024, 8, 15):
        print(match)

    print("\n\nLive matches")
    for match in get_live_matches():
        print(match)

    print("\n\nUpcoming matches")
    for match in get_upcoming_matches():
        print(f"{match.home_team} vs {match.away_team} - {match.start_date} - {match.start_time}")
=======
def get_url(year: int, month: int, day: int) -> str:
    return f"https://data.ncaa.com/casablanca/scoreboard/soccer-women/d1/{year}/{month:02}/{day:02}/scoreboard.json"

def get_urls(start_date: str) -> list[str]:
    # From the specified start date to the current date return a list of URL's for each day.
    urls = []

    current_date = datetime.datetime.now()
    start_date = datetime.datetime.strptime(start_date, "%Y/%m/%d")


    return urls



if __name__ == '__main__':
    url = get_url(2024, 8, 15)



    response = requests.get(url)
    data = response.json()

    print(data)
>>>>>>> 000d4ad (chore: wip)
