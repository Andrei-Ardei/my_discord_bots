from datetime import datetime, date, timedelta, time
import csv
import os


def parse_online_dictionary_results(word_definition_list) -> list[str]:
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
            ["/", "home", "pi", "git_projects", "my_discord_bots", "skillet_data.csv"])
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
