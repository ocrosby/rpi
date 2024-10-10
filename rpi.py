import click
import requests

def get_gist_file_content(gist_name: str, token: str):
    headers = {
        "Authorization": f"token {token}"
    }
    # List all gists
    response = requests.get("https://api.github.com/gists", headers=headers)
    gists = response.json()

    # Find the gist by name
    for gist in gists:
        if gist_name in gist['description']:
            # Assuming the file name is the same as the gist name
            file_name = f"{gist_name}.txt"
            if file_name in gist['files']:
                # Download the file
                file_url = gist['files'][file_name]['raw_url']
                file_response = requests.get(file_url)
                return file_response.text

    return None

def get_gist_file_suffix_content(gender, division, suffix, token):
    gist_name = f"{gender}_{division}_{suffix}.csv"
    return get_gist_file_content(gist_name, token)


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
    matches = get_gist_file_suffix_content(gender, division, "matches", token)
    team_conference_map = get_gist_file_suffix_content(gender, division, "team_conference_map", token)
    team_rpi = get_gist_file_content("rpi.csv", token)

    # Add your logic here to summarize RPI results

if __name__ == "__main__":
    cli()