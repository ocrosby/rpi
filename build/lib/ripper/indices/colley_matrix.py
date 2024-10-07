from typing import List, Tuple

import numpy as np

from ripper.indices.base import BaseIndex
from ripper.models.match import Match
from ripper.tools import list_team_names


class ColleyMatrixIndex(BaseIndex[float]):
    """
    This class calculates the Colley Matrix index for each team.
    """

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, float]]:
        """
        Calculate the Colley Matrix index for each team.
        :param matches: List of match results
        :return: List of tuples containing rank, team name, and rating
        """
        teams = list_team_names(matches)
        team_index = {team: idx for idx, team in enumerate(teams)}
        n = len(teams)

        C = np.identity(n) * 2
        b = np.ones(n)

        for match in matches:
            home_idx = team_index[match.home_team]
            away_idx = team_index[match.away_team]

            C[home_idx, home_idx] += 1
            C[away_idx, away_idx] += 1
            C[home_idx, away_idx] -= 1
            C[away_idx, home_idx] -= 1

            if match.home_score > match.away_score:
                b[home_idx] += 0.5
                b[away_idx] -= 0.5
            else:
                b[home_idx] -= 0.5
                b[away_idx] += 0.5

        r = np.linalg.solve(C, b)
        team_ratings = {team: round(rating, 2) for team, rating in zip(teams, r)}

        sorted_teams = sorted(team_ratings.items(), key=lambda x: (-x[1], x[0]))
        result = [
            (i + 1, team, rating) for i, (team, rating) in enumerate(sorted_teams)
        ]

        return result
