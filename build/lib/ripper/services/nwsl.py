import requests

from ripper.models.match import Match
from ripper.tools import get_start_date_and_time


class DataSource:
    def __init__(self):
        pass

    def get_matches(self) -> list[Match]:
        url = "https://api-sdp.nwslsoccer.com/v1/nwsl/football/seasons/nwsl::Football_Season::fe17bea0b7234cf7957c7249cb828270/matches?locale=en-US"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        json_data = response.json()

        json_matches = json_data.get("matches", [])
        matches = []
        for json_match in json_matches:
            status = json_match.get("status")
            if status != "FINISHED":
                continue

            json_home_team = json_match.get("home")
            home_team = json_home_team.get("officialName")
            home_score = json_match.get("homeScorePush")

            json_away_team = json_match.get("away")
            away_team = json_away_team.get("officialName")
            away_score = json_match.get("awayScorePush")

            match_date_utc = json_match.get("matchDateUtc")
            start_date, start_time = get_start_date_and_time(match_date_utc)

            match = Match(
                home_team=home_team,
                away_team=away_team,
                home_score=home_score,
                away_score=away_score,
                start_date=start_date,
                start_time=start_time,
                game_state="final",
            )

            matches.append(match)

        return matches


if __name__ == "__main__":
    source = DataSource()
    matches = source.get_matches()

    for match in matches:
        print(match)
