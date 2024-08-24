"""
This module contains utility functions that are used in the project.
"""
import csv


def decompose_stats(stats: dict) -> list[tuple[str, dict]]:
    """
    Decompose the statistics into a list of tuples containing the team name and the statistics

    :param stats:
    :return: List of tuples containing the team name and the statistics
    """
    return [(team_name, stats[team_name]) for team_name in stats]


def sort_stats(stats: dict) -> list[tuple[str, dict]]:
    """
    Sort the statistics by the 'rpi' value in decending order and then by team name alphabetically

    :param stats:
    :return: List of tuples containing the team name and the statistics
    """
    return sorted(stats.items(), key=lambda item: (-item[1]['rpi'], item[0]))


def save_stats_to_csv(filename: str, stats_list: list[tuple[str, dict]]):
    """
    Save the statistics to a CSV file

    :param filename:
    :param stats_list: List of tuples containing the team name and the statistics
    :return:
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['team', 'wins', 'losses', 'draws', 'wp', 'owp', 'oowp', 'rpi'])

        for current_team_name, current_team_statistics in stats_list:
            writer.writerow([
                current_team_name,
                current_team_statistics["wins"],
                current_team_statistics["losses"],
                current_team_statistics["draws"],
                current_team_statistics["wp"],
                current_team_statistics["owp"],
                current_team_statistics["oowp"],
                current_team_statistics["rpi"]
            ])

