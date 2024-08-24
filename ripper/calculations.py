from typing import Optional

from rpi.models.match import Match


def get_wins_for_team(matches: list[Match], team_name: str, skip_team_name: Optional[str]) -> int:
    """
    Calculate the number of wins for a specific team

    :param matches:
    :param team_name:
    :return:
    """
    wins = 0
    for match in matches:
        if not match.is_finished():
            continue

        if not match.contains(team_name):
            continue

        if skip_team_name and len(skip_team_name) > 0 and match.contains(skip_team_name):
            continue

        if match.winner() == team_name:
            wins += 1

    return wins


def get_losses_for_team(matches: list[Match], team_name: str, skip_team_name: Optional[str]) -> int:
    """
    Calculate the number of losses for a specific team

    :param matches:
    :param team_name:
    :return:
    """
    losses = 0
    for match in matches:
        if not match.is_finished():
            continue

        if not match.contains(team_name):
            continue

        if skip_team_name and len(skip_team_name) > 0 and match.contains(skip_team_name):
            continue

        if match.loser() == team_name:
            losses += 1

    return losses


def get_draws_for_team(matches: list[Match], team_name: str, skip_team_name: Optional[str]) -> int:
    """
    Calculate the number of draws for a specific team

    :param matches:
    :param team_name:
    :return:
    """
    draws = 0
    for match in matches:
        if not match.is_finished():
            continue

        if not match.contains(team_name):
            continue

        if skip_team_name and len(skip_team_name) > 0 and match.contains(skip_team_name):
            continue

        if match.is_draw():
            draws += 1

    return draws


def get_opponents(matches: list[Match], team: str) -> list[str]:
    """
    Get a list of opponents for a specific team

    :param matches:
    :param team:
    :return:
    """
    opponents = []
    for match in matches:
        if not match.is_finished() and not match.contains(team):
            continue

        if match.home_team == team:
            opponents.append(match.away_team)

        if match.away_team == team:
            opponents.append(match.home_team)

    return opponents


def get_meeting_count(team1: str, team2: str, matches: list[Match]) -> int:
    """
    Get the number of times two teams have met

    :param team1:
    :param team2:
    :param matches:
    :return: The number of times the two teams have met
    """
    count = 0
    for match in matches:
        if not match.is_finished():
            continue

        if not match.contains(team1):
            continue

        if not match.contains(team2):
            continue

        count += 1

    return count


def get_matches_played_by_team(team: str, matches: list[Match]) -> list[Match]:
    """
    Get all matches played by a specific team

    :param team: The team to get matches for
    :param matches: The list of matches to search
    :return:
    """
    team_matches = []
    for match in matches:
        if match.contains(team):
            team_matches.append(match)

    return team_matches


def get_total_matches_played_by_team(team: str, matches: list[Match]) -> int:
    """
    Get the total number of matches played by a specific team

    :param team: The team to get matches for
    :param matches: The list of matches to search
    :return:
    """
    return len(get_matches_played_by_team(team, matches))


def wp(matches: list[Match], target_team_name: str, skip_team_name: Optional[str], ndigits: int = 2) -> float:
    """
    Calculate the winning percentage for a specific team

    :param matches:
    :param target_team_name:
    :param skip_team_name: Skip this team when calculating the winning percentage
    :param ndigits: Number of digits to round to
    :return:
    """
    wins = get_wins_for_team(matches, target_team_name, skip_team_name)
    losses = get_losses_for_team(matches, target_team_name, skip_team_name)
    draws = get_draws_for_team(matches, target_team_name, skip_team_name)
    team_total_matches_played = wins + losses + draws

    result = (float(wins)+(float(draws)/2)) / float(team_total_matches_played)
    result = round(result, ndigits)

    return result


def owp(matches: list[Match], target_team_name: str, ndigits: int = 2) -> float:
    """
    Calculate the opponents' winning percentage for a specific team

    :param matches:
    :param target_team_name:
    :return:
    """
    opponent_names = get_opponents(matches, target_team_name)

    opponent_winning_percentage_dict = {}
    for opponent_name in opponent_names:
        # compute the wins for this opponent
        opponent_wins = get_wins_for_team(matches=matches, team_name=opponent_name, skip_team_name=target_team_name)
        opponent_losses = get_losses_for_team(matches=matches, team_name=opponent_name, skip_team_name=target_team_name)
        opponent_draws = get_draws_for_team(matches=matches, team_name=opponent_name, skip_team_name=target_team_name)
        total_matches_played = opponent_wins + opponent_losses + opponent_draws

        if total_matches_played == 0:
            continue

        # compute the winning percentage for this opponent
        opponent_winning_percentage = (float(opponent_wins)+(float(opponent_draws)/2)) / float(total_matches_played)

        opponent_winning_percentage_dict[opponent_name] = opponent_winning_percentage

    sum_so_far = float(0)
    number_of_matches = 0
    for oppenent_name, winning_percentage in opponent_winning_percentage_dict.items():
        meeting_count = get_meeting_count(target_team_name, oppenent_name, matches)
        number_of_matches += meeting_count
        sum_so_far += winning_percentage * float(meeting_count)

    if number_of_matches == 0:
        return float(0)

    average = sum_so_far / float(number_of_matches)
    average =  round(average, ndigits)

    return average


def oowp(matches: list[Match], target_team_name: str, ndigits: int = 2) -> float:
    """
    Calculate the opponents' opponents' winning percentage for a specific team

    :param matches:
    :param target_team_name:
    :return:
    """

    opponent_names = get_opponents(matches, target_team_name)

    opponents_owp_dict = {}
    for opponent_name in opponent_names:
        opponents_owp_dict[opponent_name] = owp(matches, opponent_name, ndigits)

    accumulator = float(0)
    number_of_matches = 0

    for opponent_name, owp_value in opponents_owp_dict.items():
        number_of_meetings = get_meeting_count(target_team_name, opponent_name, matches)
        number_of_matches += number_of_meetings
        accumulator += owp_value * float(number_of_meetings)

    average = accumulator / float(number_of_matches)

    return round(average, ndigits)


def rpi(wp_value: float, owp_value: float, oowp_value: float, ndigits: int = 2) -> float:
    """
    Calculate the RPI value for a team

    :param wp_value:
    :param owp_value:
    :param oowp_value:
    :return:
    """
    result = (wp_value * 0.25) + (owp_value * 0.50) + (oowp_value * 0.25)
    result = round(result, ndigits)

    return result
