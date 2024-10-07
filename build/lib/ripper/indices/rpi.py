"""
This module contains the RPI index class.
"""

from typing import List, Tuple

from ripper.calculations import oowp, owp, rpi, wp
from ripper.indices.base import BaseIndex
from ripper.models.match import Match
from ripper.tools import list_team_names


class RPIIndex(BaseIndex[float]):
    precision: int

    """
    This class calculates the RPI index for each team.
    """

    def __init__(self, precision: int = 2):
        self.precision = precision

    def calculate(self, matches: List[Match]) -> List[Tuple[int, str, float]]:
        """
        Calculate the RPI index for each team.
        :param matches:
        :return:
        """
        result = []

        team_names = list_team_names(matches)
        team_rpi = {}
        for current_team_name in team_names:
            wp_value = wp(matches, current_team_name, None, self.precision)
            owp_value = owp(matches, current_team_name, self.precision)
            oowp_value = oowp(matches, current_team_name, self.precision)
            rpi_value = rpi(wp_value, owp_value, oowp_value, self.precision)
            team_rpi[current_team_name] = rpi_value

        sorted_teams = sorted(team_rpi.items(), key=lambda x: (-x[1], x[0]))
        result = [(i + 1, team, rpi) for i, (team, rpi) in enumerate(sorted_teams)]

        return result
