import requests

def main_query(args: str):
    """
The main query. This is where we perform the request, read the status code and output a message
    """
    #declare url, endpoint, api
    output = "blank"
    apikey = "b48cea7bcc5fe145e290b58d3d845424"
    endpoint = "https://api.openweathermap.org/data/2.5/weather"
    parameters = {
        "appid":apikey,
        "q":args,
        "unit":"metric"
        }
    #perform query using args
    r = requests.get(url=endpoint,params=parameters)
    #output result
    return r

def unpack_response(args: str):
    response = main_query(args)
    json_response = response.json()
    if response.status_code != 200:
        return response.text
    else:
        results_dictionary = {
            "cur_temp":"{:.1f}".format(json_response["main"]["temp"] - 273.15),
            "min_temp":"{:.1f}".format(json_response["main"]["temp_min"] - 273.15),
            "max_temp":"{:.1f}".format(json_response["main"]["temp_max"] - 273.15),
            "pressure":str(json_response["main"]["pressure"]),
            "humidity":str(json_response["main"]["humidity"]),
            "wind_speed":str(json_response["wind"]["speed"]),
            "cloudiness":str(json_response["weather"][0]["description"]),
            "weather_icon":f"https://openweathermap.org/img/wn/{str(json_response['weather'][0]['icon'])}@2x.png"} 
        return results_dictionary
    
