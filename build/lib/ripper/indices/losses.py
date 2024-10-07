"""
This module contains the LossesIndex class.
"""

from typing import List, Tuple

from ripper.indices.base import BaseIndex
from ripper.models.match import Match
from ripper.tools import list_team_names


class LossesIndex(BaseIndex[int]):
    """
    Calculate the number of losses for each team
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, int]]:
        """
        Calculate the number of losses for each team
        :param matches:
        :return:
        """
        team_losses = {team_name: 0 for team_name in list_team_names(matches)}

        # Calculate Team Losses
        for match in matches:
            team_losses[match.loser()] += 1

        result = [
            (i + 1, team, losses)
            for i, (team, losses) in enumerate(team_losses.items())
        ]

        return sorted(result, key=lambda x: (x[2], x[1]))
