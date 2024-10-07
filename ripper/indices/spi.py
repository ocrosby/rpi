"""
This module contains the SPIIndex class.

•	Overview: Developed by FiveThirtyEight, the Soccer Power Index (SPI) is a rating system that estimates the strength of teams based on both their offensive and defensive abilities.
•	How It Works: SPI combines historical data, recent performance, and various statistical measures to generate a power rating for each team. It also uses a predictive model to estimate future performance, including match outcomes.
•	Implementation: You can start by gathering data on team performance metrics such as goals scored, goals conceded, and strength of opposition. The model uses these to adjust ratings after each match.
"""

from typing import List, Tuple
from ripper.models.match import Match
from ripper.indices.base import BaseIndex
from ripper.utils import list_team_names


class SPIIndex(BaseIndex[float]):
    precision: int

    """
    Calculate the Soccer Power Index for each team
    
    1. Initialize Team SPI: Create a dictionary to store the SPI for each team.
    2. Calculate Team SPI: Iterate through the matches and update the SPI for each team based on goals scored and goals conceded.
    3. Adjust SPI: Use a predictive model to adjust the SPI based on the strength of opposition and other factors.
    4. Convert to List of Tuples: Convert the dictionary to a list of tuples, where each tuple contains the team name and its SPI.
    5. Sort the List: Sort the list by SPI in descending order and then by team name in ascending order.
    6. Generate Result: Create a list of tuples containing the rank, team name, and SPI.    
    """

    def calculate(
        self, matches: List[Match], precision: int = 2
    ) -> List[Tuple[int, str, float]]:
        self.precision = precision

        # Initialize Team SPI
        team_names = list_team_names(matches)
        team_spi = {team_name: 0 for team_name in team_names}

        # Calculate Team SPI
        for match in matches:
            team_spi[match.home_team] += match.home_score
            team_spi[match.away_team] += match.away_score

        result = [(i + 1, team, spi) for i, (team, spi) in enumerate(team_spi.items())]

        return sorted(result, key=lambda x: (-x[2], x[1]))
