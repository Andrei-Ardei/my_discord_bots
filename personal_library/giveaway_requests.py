import requests

from datetime import datetime, date,timedelta

def get_giveaways():
    url = 'https://www.gamerpower.com/api/giveaways'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        filtered_giveaways = []
        for giveaway in data:
            published_date_str = giveaway['published_date']  # Get the published date from the response
        
            published_date = datetime.strptime(published_date_str, '%Y-%m-%d %H:%M:%S').date()
            today = date.today()

            #this is used for troubleshooting - uncomment and alter the days to look into a different day, then change the today from the if condition below to the previous_day
            #previous_day = today - timedelta(days=8)   

            if published_date == today:
                #print("Today's date matches the published date!")
                filtered_giveaways.append(giveaway)
            else:
                #print("Today's date does not match the published date.")
                pass
        return filtered_giveaways
    else:
        print('Error occurred. Status code:', response.status_code)
    return []