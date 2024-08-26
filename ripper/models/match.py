from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class GameState(Enum):
    PRE = "pre"
    LIVE = "live"
    FINAL = "final"


@dataclass
class Match:
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    start_date: str
    start_time: str
    game_state: str

    def __init__(self,
                 home_team: str,
                 away_team: str,
                 home_score: int,
                 away_score: int,
                 start_date: Optional[str] = None,
                 start_time: Optional[str] = None,
                 game_state: Optional[str] = None):
        self.home_team = home_team
        self.away_team = away_team
        self.home_score = home_score
        self.away_score = away_score
        self.start_date = start_date if start_date else datetime.now().strftime('%Y-%m-%d')
        self.start_time = start_time if start_time else datetime.now().strftime('%H:%M:%S')
        self.game_state = 'final' if not game_state else game_state

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} - {self.home_score} - {self.away_score} - {self.start_date} - {self.start_time} - '{self.game_state}'"

    def is_live(self):
        return self.game_state == "live"

    def is_finished(self):
        return self.game_state == "final"

    def is_upcoming(self):
        return self.game_state == "pre"

    def winner(self) -> Optional[str]:
        if not self.is_finished():
            return None

        if self.home_score > self.away_score:
            return self.home_team

        if self.away_score > self.home_score:
            return self.away_team

        return None

    def loser(self) -> Optional[str]:
        if not self.is_finished():
            return None

        if self.home_score < self.away_score:
            return self.home_team

        if self.away_score < self.home_score:
            return self.away_team

        return None

    def is_draw(self) -> bool:
        if not self.is_finished():
            return False

        return self.home_score == self.away_score

    def contains(self, team: str) -> bool:
        return team in [self.home_team, self.away_team]
