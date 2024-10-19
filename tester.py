import helper


if __name__ == "__main__":
    author_id = '243365137795383297'
    results = helper.get_elements_by_author_id(
        helper.notifications_json_file, author_id)
    game_titles = [game['app_name'] for game in results]
    for result in game_titles:
        print(result)
