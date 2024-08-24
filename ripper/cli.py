from datetime import datetime

import click

from rpi.models.match import Match
from rpi.services.match import save_matches_to_csv, calculate_statistics, save_stats_to_csv, get_matches_on

@click.group()
def cli():
    pass


@cli.command()
@click.option('--year', type=int, required=True, help='Year of the matches')
@click.option('--month', type=int, required=True, help='Month of the matches')
@click.option('--day', type=int, required=True, help='Day of the matches')
def matches(year, month, day):
    """
    Get the matches on a specific date

    :param year:
    :param month:
    :param day:
    :return:
    """
    date = datetime(year, month, day)
    my_matches: list[Match] = get_matches_on(date, "live")
    for match in my_matches:
        click.echo(match)

if __name__ == '__main__':
    cli()
