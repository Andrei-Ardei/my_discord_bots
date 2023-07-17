import requests
import json
import os

def query_dictionary(cuvant):

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{cuvant}"

    payload = {}
    headers = {

    }

    response = requests.get(url, headers=headers, data=payload)

    almanach = []
    if response.status_code == 200:
        almanach = response.json()

    elif response.status_code == 404:
        almanach = response.json()
        


    return almanach
