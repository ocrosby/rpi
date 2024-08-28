from datetime import datetime


from typing import List, Callable, Dict, Any, Tuple
from ripper.indices.base import BaseIndex
from ripper.models.match import Match
from ripper.

class Simulation:
    def __init__(self, indices: List[BaseIndex], measurement_function: Callable[[List, List], float]):
        self.indices = indices
        self.measurement_function = measurement_function

    def run(self, matches: List[Match], correct_ranks: List[Tuple[int, str]]) -> Dict[str, float]:
        results = {}
        for index in self.indices:
            index_name = index.__class__.__name__
            calculated_ranks = index.calculate(matches)
            accuracy = self.measurement_function(calculated_ranks, correct_ranks)
            results[index_name] = accuracy

        return results


if __name__ == "__main__":
    from ripper.indices.matches_played import MatchesPlayedIndex
    from ripper.indices.wins import WinsIndex
    from ripper.indices.win_percentage import WinPercentageIndex
    from ripper.utils import list_team_names, calculate_accuracy

    indices = [MatchesPlayedIndex(), WinsIndex(), WinPercentageIndex()]
    simulation = Simulation(indices, calculate_accuracy)

    # Load Matches
    matches = Match.load_from_file("data/matches.csv")

    # Load Correct Ranks
    correct_ranks = [(1, "Team A"), (2, "Team B"), (3, "Team C")]

    # Run Simulation
    results = simulation.run(matches, correct_ranks)

    # Print Results
    for index_name, accuracy in results.items():
        print(f"{index_name}: {accuracy}")