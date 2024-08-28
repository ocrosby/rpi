import os
import csv
import sys

import click
import requests

import ripper.services.ncaa as ncaa_service

from ripper.models.match import Match
from ripper.utils import save_matches_to_csv
from ripper.elo import process_matches_with_elo
from ripper.indices.rpi import RPIIndex
from ripper.indices.record import RecordIndex


def common_options(func):
    """
    Decorator to add common options to CLI commands.
    """
    func = click.option('-s', '--source', type=click.Choice(['ncaa', 'ecnl', 'ga', 'nwsl', 'mls']), default='ncaa', help='Source of the matches')(func)
    func = click.option('-o', '--output', type=click.Path(), default=None, help='Output file for the matches (defaults to standard output)')(func)
    func = click.option('-d', '--start_date', type=click.DateTime(formats=["%Y-%m-%d"]), default=None, help='Start date for the matches in YYYY-MM-DD format, defaults to start of season')(func)

    return func

@click.group()
def cli():
    pass


def find_gist_by_filename(token, filename):
    """
    Find a Gist by filename.
    """
    response = requests.get(
        'https://api.github.com/gists',
        headers={'Authorization': f'token {token}'}
    )

    if response.status_code != 200:
        print('Failed to retrieve gists')
        print(response.json())
        sys.exit(1)

    gists = response.json()
    for gist in gists:
        if filename in gist['files']:
            return gist['id']
    return None

def post_or_patch_gist(file_path, description, public, token):
    """
    Post or patch a CSV file to a Gist.
    """
    if not token:
        print('GitHub token is required. Set it using --token option or GITHUB_TOKEN environment variable.')
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    gist_data = {
        'description': description,
        'public': public,
        'files': {
            os.path.basename(file_path): {
                'content': content
            }
        }
    }

    gist_id = find_gist_by_filename(token, os.path.basename(file_path))

    if gist_id:
        response = requests.patch(
            f'https://api.github.com/gists/{gist_id}',
            json=gist_data,
            headers={
                'Authorization': f'token {token}',
                'Content-Type': 'application/json'
            }
        )
        action = 'patched'
    else:
        response = requests.post(
            'https://api.github.com/gists',
            json=gist_data,
            headers={
                'Authorization': f'token {token}',
                'Content-Type': 'application/json'
            }
        )
        action = 'created'

    if response.status_code in [200, 201]:
        print(f'Gist {action} successfully!')
        print(response.json()['html_url'])
    else:
        print(f'Failed to {action} Gist')
        print(response.json())
        sys.exit(1)

@cli.command('post')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('-d', '--description', default='CSV file', help='Description of the Gist')
@click.option('--public', is_flag=True, help='Make the Gist public')
@click.option('--token', envvar='GITHUB_TOKEN', help='GitHub token for authentication')
def post_gist(file_path, description, public, token):
    """
    Post a CSV file to a Gist
    """
    post_or_patch_gist(file_path, description, public, token)


@cli.command('record')
@common_options
def record(source, output, start_date):
    """
    Calculate records for each team.
    """
    if source == 'ncaa':
        if not start_date:
            start_date = ncaa_service.SEASON_START_DATE

        # Check to see if the matches.csv file exists, if it does, use that instead of the API
        if os.path.exists('matches.csv'):
            with open('matches.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                my_matches = [Match(*row) for row in reader]
        else:
            my_matches: list[Match] = ncaa_service.get_matches_from(start_date, state='final')

            # Save the matches to a CSV file
            save_matches_to_csv('matches.csv', my_matches, 'final')

        # Calculate the record
        record_index = RecordIndex()
        results = record_index.calculate(my_matches)

        if output:
            with open(output, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Rank', 'Team', 'RPI'])
                for rank, team, rpi in results:
                    writer.writerow([rank, team, rpi])
        else:
            for rank, team, record in results:
                click.echo(f"#{rank} Team: '{team}', Record: {record}")

    else:
        raise NotImplementedError(f"The {source} data source is not implemented yet")


@cli.command('elo')
@common_options
def elo(source, output, start_date):
    """
    Calculate ratings based on the Elo rating system.
    """
    if source == 'ncaa':
        if not start_date:
            start_date = ncaa_service.SEASON_START_DATE

        # Check to see if the matches.csv file exists, if it does, use that instead of the API
        if os.path.exists('matches.csv'):
            with open('matches.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                my_matches = [Match(*row) for row in reader]
        else:
            my_matches: list[Match] = ncaa_service.get_matches_from(start_date, state='final')

            # Save the matches to a CSV file
            save_matches_to_csv('matches.csv', my_matches, 'final')

        # Calculate the Elo ratings
        results = process_matches_with_elo(my_matches)
    else:
        raise NotImplementedError(f"The {source} data source is not implemented yet")


    # Sort results by rating in descending order
    sorted_results = sorted(results.items(), key=lambda item: item[1], reverse=True)

    if output:
        with open(output, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Rank', 'Team', 'Rating'])
            for index, (team, rating) in enumerate(sorted_results, start=1):
                writer.writerow([index, team, rating])

    else:
        for index, (team, rating) in enumerate(sorted_results, start=1):
            click.echo(f"#{index} Team: '{team}', Rating: {rating}")


@cli.command('rpi')
@common_options
def rpi(source, output, start_date):
    """
    Calculate ratings based on the RPI rating system.
    """
    if source == 'ncaa':
        if not start_date:
            start_date = ncaa_service.SEASON_START_DATE

        # Check to see if the matches.csv file exists, if it does, use that instead of the API
        if os.path.exists('matches.csv'):
            with open('matches.csv', mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Skip the header row
                my_matches = [Match(*row) for row in reader]
        else:
            my_matches: list[Match] = ncaa_service.get_matches_from(start_date, state='final')

            # Save the matches to a CSV file
            save_matches_to_csv('matches.csv', my_matches, 'final')

        # Calculate the RPI index
        rpi_index = RPIIndex(2)
        results = rpi_index.calculate(my_matches)

        if output:
            with open(output, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Rank', 'Team', 'RPI'])
                for rank, team, rpi in results:
                    writer.writerow([rank, team, rpi])
        else:
            for rank, team, rating in results:
                click.echo(f"#{rank} Team: '{team}', RPI: {rating}")

    else:
        raise NotImplementedError(f"The {source} data source is not implemented yet")

@cli.command('matches')
@click.option('-t', '--state', type=click.Choice(['final', 'live', 'pre']), default=None, help='State of the matches (final, live, pre), defaults to final', required=False)
@common_options
def matches(source, state, output, start_date):
    """
    Get the matches from the specified date until today.

    Note: This command defaults to the start of the most recent season.
    """
    if source == 'ncaa':
        if state is None:
            state = 'final'

        if not start_date:
            start_date = ncaa_service.SEASON_START_DATE

        my_matches: list[Match] = ncaa_service.get_matches_from(start_date, state=state)
    else:
        raise NotImplementedError(f"The {source} data source is not implemented yet")

    if output:
        save_matches_to_csv(output, my_matches, state)
    else:
        for match in my_matches:
            click.echo(match)


if __name__ == '__main__':
    cli()
