import requests
import logging

#Use openweathermap.org to get weather forecast.  This is a login
#key generated for a free account on their site.  
OPENWEATHER_KEY = '<Key Here>'

#Latitude and Longitude of Sean's House
LAT = '39.03'
LON = '-77.38'

#Request to fetch the forecast.  Returns 3 hour increment forecast for next 5 days.
url = f'http://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={OPENWEATHER_KEY}'


#Make web request to get weather forecast.  Return the predicted milimeters of
#precip in the next 24 hours.
def checkRainPrediction():
    log = logging.getLogger()
    
    #Make web request
    response = requests.get(url)

    precip = 0.0
    if response.status_code == 200:
        #Parse the JSON reply
        data = response.json()
    
        #We are interested in precipitation for the next 24 hours,
        #so read 8 of the 3 hour forecasts
        num_forecasts = 0
        for forecast in data['list']:
            if 'rain' in forecast:
                precip += float(forecast['rain']['3h'])
            num_forecasts += 1
        
            if num_forecasts >= 8:
                break
    else:
        log.error('Error fetching weather data. ' + response)
    
    log.info('Predicted rain in next 24 hours: ' + str(precip) + " milimeters")
    return precip
  