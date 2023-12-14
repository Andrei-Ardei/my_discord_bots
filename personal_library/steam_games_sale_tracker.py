import requests
import json
from bs4 import BeautifulSoup
import re
from datetime import datetime


def get_app_list():
    url = "http://api.steampowered.com/ISteamApps/GetAppList/v2/"

    payload = {}
    headers = {
        'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return "There was a problem fetching the list."


def get_app_details(app_id, cc_param):
    url = f"https://store.steampowered.com/api/appdetails?appids={str(app_id)}&cc={cc_param}"

    payload = {}
    headers = {
        'Accept': 'application/json'
    }
    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return "There was a problem fetching the app details."


def fetch_list_of_games_by_name(app_name: str):
    """Used to fetch the list of games based on a string search"""
    list_of_games = get_app_list()
    found_games = []
    for game in list_of_games['applist']['apps']:
        if app_name.lower() in game['name'].lower():
            found_games.append(game)
    print(f"{len(found_games)} games found...")

    return found_games


def get_final_discount_date_for_app(app_id):
    url = f"https://store.steampowered.com/app/{app_id}"

    payload = {}
    headers = {
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the text content from the HTML element
        element_text = soup.find(
            'p', class_='game_purchase_discount_countdown').get_text()

        # Use a regular expression to find the date (assuming the date format is consistent)
        date_match = re.search(r'(\d+\s+\w+)$', element_text)

        if date_match:
            sale_end_date_str = date_match.group(1)

            # Parse the extracted date string into a datetime object
            # sale_end_datetime = datetime.strptime(sale_end_date_str, '%d %B')
            return sale_end_date_str
