import csv
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from ripper.models.score import Score
from ripper.models.team import Team


class CrossDivisionMatchException(Exception):
    """Exception raised for cross-division matches."""
    def __init__(self, home_team: str, away_team: str, home_division: str, away_division: str):
        self.home_team = home_team
        self.away_team = away_team
        self.home_division = home_division
        self.away_division = away_division
        super().__init__(f"Cross-division match detected: {home_team} ({home_division}) vs {away_team} ({away_division})")


class Match(BaseModel):
    gender: Optional[str] = Field(default=None)
    home: Team
    away: Team
    score: Score = Score()
    date: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d")
    )
    time: Optional[str] = Field(
        default_factory=lambda: datetime.now().strftime("%H:%M:%S")
    )
    status: Optional[str] = None

    @model_validator(mode='after')
    def check_scores(cls, values):
        if values.status == 'pre':
            return values
        if values.score.home is None or values.score.away is None:
            raise ValueError("home and away cannot be empty unless status is 'pre'")
        return values

class MatchDecorator:
    """
    Decorator class for Match objects
    """

    def __init__(self, match: Match):
        """
        Constructor for MatchDecorator class
        :param match:
        """
        self.match = match

    def __str__(self):
        """
        String representation of the MatchDecorator object

        :return:
        """
        return f"{self.match.home.name} vs. {self.match.away.name} ({self.match.score.home} - {self.match.score.away})"

    def is_live(self):
        return self.match.status == "live"

    def is_finished(self):
        return self.match.status in ["finished", "final"]

    def is_upcoming(self):
        return self.match.status == "pre"

    def winner(self) -> Optional[str]:
        if not self.is_finished():
            return None

        if self.match.score.home > self.match.score.away:
            return self.match.home.name

        if self.match.score.away > self.match.score.home:
            return self.match.away.name

        return None

    def loser(self) -> Optional[str]:
        if not self.is_finished():
            return None

        if self.match.score.home < self.match.score.away:
            return self.match.home.name

        if self.match.score.away < self.match.score.home:
            return self.match.away.name

        return None

    def is_draw(self) -> bool:
        if not self.is_finished():
            return False

        return self.match.score.home == self.match.score.away

    def contains(self, team: str) -> bool:
        return team in [self.match.home.name, self.match.away.name]

    @staticmethod
    def decorate(match: Match):
        return MatchDecorator(match)


