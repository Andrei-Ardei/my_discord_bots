import requests

from datetime import datetime, date,timedelta

def get_giveaways():
    url = 'https://www.gamerpower.com/api/giveaways'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        published_date_str = data[0]['published_date']  # Get the published date from the response
    
        published_date = datetime.strptime(published_date_str, '%Y-%m-%d %H:%M:%S').date()
        today = date.today()

        previous_day = today - timedelta(days=1)    
        
        if published_date == previous_day:
            print("Today's date matches the published date!")
            return data[0]
        else:
            print("Today's date does not match the published date.")
    else:
        print('Error occurred. Status code:', response.status_code)

giveaways_data = get_giveaways()
print(giveaways_data)