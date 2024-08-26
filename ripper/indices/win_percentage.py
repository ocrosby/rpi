"""
This module contains the WinPercentageIndex class.
"""

from typing import List, Tuple
from ripper.models.match import Match
from ripper.indices.base import BaseIndex
from ripper.utils import list_team_names
from ripper.indices.wins import WinsIndex
from ripper.indices.matches_played import MatchesPlayedIndex


class WinPercentageIndex(BaseIndex[float]):
    wins_index: WinsIndex
    matches_played_index: MatchesPlayedIndex

    def __init__(self):
        self.wins_index = WinsIndex()
        self.matches_played_index = MatchesPlayedIndex()

    """
    Calculate the win percentage for each team
    """
    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, float]]:
        """
        Calculate the win percentage for each team
        :param matches:
        :return:
        """
        wins = self.wins_index.calculate(matches)
        matches_played = self.matches_played_index.calculate(matches)

        team_win_percentage = {team_name: float(0) for team_name in list_team_names(matches)}

        # for each key in the team_win_percentage dictionary, calculate the win percentage
        for team_name, _ in team_win_percentage.items():
            for i in range(len(wins)):
                if wins[i][1] == team_name:
                    team_win_percentage[team_name] = wins[i][2] / matches_played[i][2]

        result = [(i + 1, team, win_percentage) for i, (team, win_percentage) in enumerate(team_win_percentage.items())]

        return sorted(result, key=lambda x: (-x[2], x[1]))

