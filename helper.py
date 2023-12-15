from datetime import datetime, date, timedelta, time
import csv
import os
import json
from personal_library import steam_games_sale_tracker as sgst


def parse_online_dictionary_results(word_definition_list):
    list_of_word_descriptions = []
    current_number = 1

    for definition in word_definition_list:
        if 'phonetic' in definition:
            list_of_word_descriptions.append(
                '\r\n## ' + definition['word'] + ' '+definition['phonetic'] + '\r\n')
        else:
            list_of_word_descriptions.append(
                '\r\n## ' + definition['word'] + '\r\n')
        for meaning in definition['meanings']:
            list_of_word_descriptions.append(
                '### ' + meaning['partOfSpeech'])
            for definitions in meaning['definitions']:

                if not 'example' in definitions:
                    list_of_word_descriptions.append(
                        str(current_number) + '. ' + definitions['definition'].capitalize())

                else:
                    list_of_word_descriptions.append(str(
                        current_number) + '. ' + definitions['definition'].capitalize() + '\r\n' + '\"_' + definitions['example'] + '_\"')

                current_number += 1
    return list_of_word_descriptions


def check_game_title(filename, game_title):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row

        for row in reader:
            date_str = row[0]  # Assuming the date is in the first column
            game_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()

            if game_date >= thirty_days_ago and game_date <= today and row[1] == game_title:
                return True  # Game title found within the past 30 days

    return False  # Game title not found within the past 30 days


def append_data_to_csv(filename, date, game_title):
    if not os.path.isfile(filename):
        # File does not exist, create a new one and write headers
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["date", "game_title"])  # Write headers
            writer.writerow([date, game_title])  # Write data
    else:
        # File exists, append data
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([date, game_title])  # Write data


def record_messages(message):
    if os.name == "nt":
        filename = os.sep.join(["skillet_data.csv"])
    elif os.name == "posix":
        filename = os.sep.join(
            ["/", "home", "menajerulrobotilor", "git_projects", "my_discord_bots", "skillet_data.csv"])
    # filename = "skillet_data.csv"

    if not os.path.isfile(filename):
        # File does not exist, create a new one and write headers
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Message"])  # Write headers
            writer.writerow([message.author, message.content])  # Write data
    else:
        # File exists, append data
        with open(filename, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([message.author, message.content])  # Write data

    # stop record messages


def dump_dict_to_json(dictionary, filename):
    try:
        # Try to open the file in read mode to check if it exists
        with open(filename, 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty list
        existing_data = []

    # Generate the next primary key based on the last item in the list
    if existing_data:
        last_item = existing_data[-1]
        next_primary_key = last_item.get('id', 0) + 1
    else:
        next_primary_key = 1

    # Add the new dictionary with the generated primary key
    dictionary['id'] = next_primary_key
    existing_data.append(dictionary)

    # Write the updated data back to the file in write mode
    with open(filename, 'w') as file:
        json.dump(existing_data, file, indent=2)


def verify_games(list_of_games):
    discounted_games = []
    for game in list_of_games:
        game_id = str(game['app_id'])
        game_details = sgst.get_app_details(game_id, game['pref_cur'])
        if game_details[game_id]['data']['price_overview']['discount_percent'] != 0:
            discount_end_date = sgst.get_final_discount_date_for_app(game_id)
            discounted_games.append(f"{game_details[game_id]['data']['name']} is currently on sale for {game_details[game_id]['data']['price_overview']['final_formatted']}, down from {game_details[game_id]['data']['price_overview']['initial_formatted']}, saving you {game_details[game_id]['data']['price_overview']['discount_percent']}%. This sale lasts until {discount_end_date}.")
            pop_the_current_subscription_if_a_discount_is_found(game['id'])
    return discounted_games


def get_elements_by_author_id(filename, target_author_id):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

    # Filter elements by matching author_id
    matching_elements = [entry for entry in data if entry.get(
        'author_id') == target_author_id]

    return matching_elements


def get_unique_author_ids(filename='notifications.json'):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        return []  # Return an empty list if the file doesn't exist

    unique_author_ids = set()  # Use a set to store unique author_ids

    for entry in data:
        author_id = entry.get('author_id')
        if author_id is not None:
            unique_author_ids.add(author_id)

    return list(unique_author_ids)


def pop_the_current_subscription_if_a_discount_is_found(sub_id):
    file_path = 'notifications.json'
    with open(file_path, 'r') as file:
        game_list = json.load(file)

    # Create a new list excluding the element with the specified id
    filtered_game_list = [game for game in game_list if game['id'] != sub_id]

    # Write the updated list back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(filtered_game_list, file, indent=2)


if __name__ == "__main__":
    discord_users = get_unique_author_ids()
    for user in discord_users:
        list_of_games = get_elements_by_author_id('notifications.json', user)
        list_of_discounts = verify_games(list_of_games)
