import requests

url = "https://sdataprod.ncaa.com/?meta=GetLiveSchedulePlusMmlEventVideo_web&extensions={%22persistedQuery%22:{%22version%22:1,%22sha256Hash%22:%225e408e8d1c9a53092ce7f07feaabb522dc1d2c6ff18a52690a1ff564ec26e3ba%22}}&variables={%22today%22:true,%20%22monthly%22:false,%20%22contestDate%22:%2208/29/2024%22,%20%22seasonYear%22:2023}"

if __name__ == "__main__":
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    # Convert the response to JSON
    json_data = response.json()

    # Print the JSON data
    print(json_data)
