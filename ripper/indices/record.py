"""
This module contains the RecordIndex class.
"""

from typing import List, Tuple
from ripper.models.match import Match
from ripper.indices.base import BaseIndex
from ripper.utils import list_team_names


class Record:
    wins: int
    losses: int
    draws: int

    def __init__(self, wins: int, losses: int, draws: int):
        self.wins = wins
        self.losses = losses
        self.draws = draws

    def __str__(self):
        return f"{self.wins}-{self.losses}-{self.draws}"

    def points(self):
        return self.wins * 3 + self.draws


class RecordIndex(BaseIndex[Tuple[int, int]]):
    """
    Calculate the record for each team
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, str]]:
        # Initialize Team Record
        team_name = list_team_names(matches)
        records = {team_name: Record(0, 0, 0) for team_name in team_name}

        # Calculate Team Record
        for match in matches:
            if match.winner() == match.home_team:
                records[match.home_team].wins += 1
                records[match.away_team].losses += 1
            elif match.winner() == match.away_team:
                records[match.away_team].wins += 1
                records[match.home_team].losses += 1
            else:
                records[match.home_team].draws += 1
                records[match.away_team].draws += 1

        # Convert to list of tuples
        result = [
            (team, record.wins, record.losses, record.draws, record.points())
            for team, record in records.items()
        ]

        # Sort by record and then by team name
        sorted_result = sorted(result, key=lambda x: (-x[4], x[0]))

        # Generate result with rank
        ranked_result = []
        rank = 1
        for team, wins, losses, draws, points in sorted_result:
            ranked_result.append((rank, team, str(Record(wins, losses, draws))))
            rank += 1

        return ranked_result
