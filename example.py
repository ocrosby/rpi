import csv
import requests

if __name__ == "__main__":
    # URL of the raw CSV file in the Gist
    url = "https://gist.githubusercontent.com/ocrosby/bbe3ecd77bafb68adedcc66ac8f5f345/raw"

    # Fetch the CSV file
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses

    # Read the CSV content
    csv_content = response.text

    # Parse the CSV content
    csv_reader = csv.DictReader(csv_content.splitlines())

    # Convert to a list of tuples
    data = [(row['Rank'], row['Team'], row['RPI']) for row in csv_reader]

    # Print the data
    for row in data:
        print(row)

    # Generate a list of team names
    team_names = [row[1] for row in data]

    # Generate a mapping of team names to RPI values
    rpi_values = {row[1]: float(row[2]) for row in data}

    # Todo: Generate a mapping of team names to conferences

