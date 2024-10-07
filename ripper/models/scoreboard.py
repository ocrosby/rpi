from typing import List, Optional

from pydantic import BaseModel


class Conference(BaseModel):
    conferenceName: str
    conferenceSeo: str


class TeamNames(BaseModel):
    char6: str
    short: str
    seo: str
    full: str


class Team(BaseModel):
    score: str
    names: TeamNames
    winner: bool
    seed: Optional[str] = ""
    description: str
    rank: Optional[str] = ""
    conferences: List[Conference]


class Game(BaseModel):
    gameID: str
    away: Team
    finalMessage: str
    bracketRound: Optional[str] = ""
    title: str
    contestName: Optional[str] = ""
    url: str
    network: Optional[str] = ""
    home: Team
    liveVideoEnabled: bool
    startTime: str
    startTimeEpoch: str
    bracketId: Optional[str] = ""
    gameState: str
    startDate: str
    currentPeriod: str
    videoState: Optional[str] = ""
    bracketRegion: Optional[str] = ""
    contestClock: str


class GameWrapper(BaseModel):
    game: Game


class RootModel(BaseModel):
    inputMD5Sum: str
    instanceId: str
    updated_at: str
    games: List[GameWrapper]
    hideRank: bool


from datetime import date

import requests


class ScoreboardDataRetriever:
    def __init__(self, gender: str, division: str, date_obj: date):
        self.gender = gender
        self.division = division
        self.date_obj = date_obj

    def build_url(self) -> str:
        return f"https://data.ncaa.com/casablanca/scoreboard/soccer-{self.gender}/{self.division}/{self.date_obj.strftime('%Y/%m/%d')}/scoreboard.json"

    def fetch(self) -> Optional[RootModel]:
        url = self.build_url()

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            data = response.json()  # Parse the JSON data
            root_model = RootModel.model_validate(
                data
            )  # Parse the JSON data into a RootModel object
            return root_model
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
        except ValueError as json_err:
            print(f"JSON decoding error: {json_err}")

        return None


if __name__ == "__main__":
    gender = "women"
    division = "d1"
    date_obj = date(2024, 10, 4)

    retriever = ScoreboardDataRetriever(gender, division, date_obj)
    root_model = retriever.fetch()

    if root_model:
        print(root_model)
