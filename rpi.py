import os
import csv
import subprocess

from io import StringIO

import click
import requests

def get_gist_file_content(gist_name: str, token: str):
    auth = ("ocrosby", token)
    # List all gists
    response = requests.get("https://api.github.com/users/ocrosby/gists", auth=auth)
    gists = response.json()

    # Find the gist by name
    for gist in gists:
        for file_name, file_info in gist['files'].items():
            if gist_name == file_name:
                # Download the file
                file_url = file_info['raw_url']
                file_response = requests.get(file_url)
                return file_response.text

    return None

def get_gist_file_suffix_content(gender, division, suffix, token):
    gist_name = f"{gender}_{division}_{suffix}.csv"
    return get_gist_file_content(gist_name, token)


def get_conference_by_team(team_conference_map, team_name):
    """
    Look up the conference given a team name.

    :param team_conference_map: List of dicts containing "Conference" and "Team Name".
    :param team_name: The name of the team to look up.
    :return: The conference of the given team name, or None if not found.
    """
    for entry in team_conference_map:
        if entry["Team Name"] == team_name:
            return entry["Conference"]
    return None


def get_teams_by_conference(team_conference_map, conference):
    """
    Retrieve a list of team names in a given conference, sorted by name.

    :param team_conference_map: List of dicts containing "Conference" and "Team Name".
    :param conference: The conference to look up.
    :return: A sorted list of team names in the given conference.
    """
    teams = [entry["Team Name"] for entry in team_conference_map if entry["Conference"] == conference]
    return sorted(teams)

def get_sorted_conference_names(team_conference_map):
    """
    Retrieve a sorted list of unique conference names from the team_conference_map.

    :param team_conference_map: List of dicts containing "Conference" and "Team Name".
    :return: A sorted list of unique conference names.
    """
    conferences = {entry["Conference"] for entry in team_conference_map}
    return sorted(conferences)


def generate_conference_rpi_file(team_rpi, conference_name, team_conference_map, token):
    """
    Generate a CSV file containing team and RPI value for a given conference,
    sorted in descending order by RPI.

    :param team_rpi: List of dicts containing "Team" and "RPI".
    :param conference_name: The name of the conference.
    :param team_conference_map: List of dicts containing "Conference" and "Team Name".
    """
    # Filter teams by conference
    teams_in_conference = get_teams_by_conference(team_conference_map, conference_name)

    # Filter RPI data for teams in the conference
    conference_rpi = [
        {"Team": entry["Team"], "RPI": float(entry["RPI"])}
        for entry in team_rpi
        if entry["Team"] in teams_in_conference
    ]

    # Sort by RPI in descending order
    conference_rpi_sorted = sorted(conference_rpi, key=lambda x: x["RPI"], reverse=True)

    # Generate the CSV file
    file_name = f"female_{conference_name}_rpi.csv"
    file_name = file_name.lower()
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")
    with open(file_name, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Team", "RPI"])
        for entry in conference_rpi_sorted:
            writer.writerow([entry["Team"], entry["RPI"]])


@click.group()
def cli():
    """
    Command line interface to summarize RPI results.
    """
    pass

@cli.command("pull")
@click.option(
    "--gender",
    type=click.Choice(["male", "female"]),
    required=True,
    help="Gender can be male or female",
)
@click.option(
    "--division",
    type=click.Choice(["d1", "d2", "d3"]),
    required=True,
    help="Division can be d1, d2, or d3",
)
@click.option(
    "--token",
    required=True,
    help="GitHub personal access token",
)
def summarize_rpi(gender: str, division: str, token: str) -> None:
    """
    Summarize RPI results by gender and division.
    """
    # Placeholder for the actual logic to summarize RPI results
    print(f"Summarizing RPI results for gender: {gender}, division: {division}")

    # Download the matches file
    matches_content = get_gist_file_suffix_content(gender, division, "matches", token)
    team_conference_map_content = get_gist_file_suffix_content(gender, division, "team_conference_map", token)
    team_rpi_content = get_gist_file_content("rpi.csv", token)

    if matches_content:
        matches = list(csv.DictReader(StringIO(matches_content)))
        print("Matches:", matches)

    team_conference_map = []
    if team_conference_map_content:
        team_conference_map = list(csv.DictReader(StringIO(team_conference_map_content)))
        print("Team Conference Map:", team_conference_map)

    team_rpi = []
    if team_rpi_content:
        team_rpi = list(csv.DictReader(StringIO(team_rpi_content)))
        print("Team RPI:", team_rpi)

    conference_names = get_sorted_conference_names(team_conference_map)

    for conference in conference_names:
        generate_conference_rpi_file(team_rpi, conference, team_conference_map, token)


    # Add your logic here to summarize RPI results
    current_directory = os.getcwd()
    # Iterate over all files in the current directory
    for file_name in os.listdir(current_directory):
        # Check if the file is a CSV file
        if file_name.endswith(".csv"):
            print(f"Posting file: {file_name}")
            try:
                subprocess.run(f'ripper post -d "{file_name}" --public --token {token} {file_name}', shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error processing file: {file_name}")
                print(e)


if __name__ == "__main__":
    cli()