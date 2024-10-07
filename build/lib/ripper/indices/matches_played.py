"""
This module contains the MatchesPlayedIndex class.
"""

from typing import List, Tuple

from ripper.indices.base import BaseIndex
from ripper.models.match import Match
from ripper.tools import list_team_names


class MatchesPlayedIndex(BaseIndex[int]):
    """
    Calculate the number of matches played for each team
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, int]]:
        """
        Calculate the number of matches played for each team
        :param matches:
        :return:
        """
        team_matches = {team_name: 0 for team_name in list_team_names(matches)}

        # Calculate Team Matches
        for match in matches:
            team_matches[match.home_team] += 1
            team_matches[match.away_team] += 1

        result = [
            (i + 1, team, matches_played)
            for i, (team, matches_played) in enumerate(team_matches.items())
        ]

        return sorted(result, key=lambda x: (-x[2], x[1]))
