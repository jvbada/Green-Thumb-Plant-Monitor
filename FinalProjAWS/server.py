from flask import Flask, request, render_template
from datetime import date, datetime
from numpy import interp
import python_weather
import asyncio

app = Flask(__name__)

# Sensor data
light = None
soilMoisture = None
temp = None
humid = None

lightFlag = None;
waterFlag = None;
tempFlag = None;

weatherText = None
weatherTemp = None
weather1Day = None
weather2Day = None

avgTemp = 0;

today = None;

async def getweather():
    global weatherTemp, weatherText, weather1Day, weather2Day, avgTemp
    # declare the client. format defaults to the metric system (celcius, km/h, etc.)
    client = python_weather.Client(format=python_weather.IMPERIAL)

    # fetch a weather forecast from a city
    weather = await client.find("Irvine CA")
    avgTemp = 0
    # returns the current day's forecast temperature (int)
    weatherText = weather.current.sky_text
    weatherTemp = weather.current.temperature
    avgTemp += weather.current.temperature

    # get the weather forecast for a few days
    i = 0
    for forecast in weather.forecasts:
        # print(str(forecast.date), forecast.sky_text, forecast.temperature)
        if (i == 2):
            weather1Day = str(forecast.date).split()[0] + " - " + str(forecast.sky_text) + " " + str(forecast.temperature)
            avgTemp += forecast.temperature
        elif (i == 3):
            weather2Day = str(forecast.date).split()[0] + " - " + str(forecast.sky_text) + " " + str(forecast.temperature)
            avgTemp += forecast.temperature
        i += 1
    
    avgTemp /= 3
    avgTemp = interp(avgTemp, [45,85], [100,1])
    avgTemp = int(avgTemp)
    print("Watering percent: " + str(avgTemp))

    # close the wrapper once done
    await client.close()


@app.route("/", methods=['GET'])
def getData():
    global light, soilMoisture, temp, humid, weatherTemp, weatherText, weather1Day, weather2Day, lightFlag, waterFlag, tempFlag, avgTemp, today

    today = date.today().strftime("%B %d, %Y")
    day = date.today().strftime("%B %d, %Y")
    time = datetime.now().strftime("%H:%M:%S")

    loop = asyncio.new_event_loop() # for Python >= 3.10, otherwise use get_event_loop
    loop.run_until_complete(getweather())

    updateLight = request.args.get("light")
    updateSoilMoisture = request.args.get("soilMoisture")
    updateTemp = request.args.get("temp")
    updateHumid = request.args.get("humid")

    if updateLight != None:
        if int(updateLight) < 500:
            lightFlag = "Put plant in sunlight"
        else:
            lightFlag = "No need to put plant in sunlight"
    else:
        lightFlag = "No need to put plant in sunlight"

    if updateSoilMoisture != None:
        if int(updateSoilMoisture) < 20:
            waterFlag = "Time to water plant"
        elif int(updateSoilMoisture) > 60:
            waterFlag = "Stop watering plant"
        else:
            waterFlag = "Good moisture level for plant"
    else:
        waterFlag = "Good moisture level for plant"

    if updateTemp != None:
        if float(updateTemp) < 60.0:
            tempFlag = "Put plant in a warmer place"
        elif float(updateTemp) > 85.0:
            tempFlag = "Put plant in a cooler place"
        else:
            tempFlag = "Good temperature for plant"
    else:
        tempFlag = "Good temperature for plant"


    # Set global variables
    light = updateLight
    soilMoisture = updateSoilMoisture
    temp = updateTemp
    humid = updateHumid
    return render_template("index.html", light=updateLight, soilMoisture=updateSoilMoisture, 
                            temp=updateTemp, humid=updateHumid, day=day, time=time, weatherText=weatherText, 
                            weatherTemp=weatherTemp, weather1Day=weather1Day, weather2Day=weather2Day, 
                            lightFlag=lightFlag, waterFlag=waterFlag, tempFlag=tempFlag,  avgTemp=avgTemp, 
                            today=today)


@app.route("/data")
def refreshData():
    global light, soilMoisture, temp, humid, weatherTemp, weatherText, weather1Day, weather2Day, lightFlag, waterFlag, tempFlag, avgTemp, today
    
    day = date.today().strftime("%B %d, %Y")
    time = datetime.now().strftime("%H:%M:%S")

    loop = asyncio.new_event_loop() # for Python >= 3.10, otherwise use get_event_loop
    loop.run_until_complete(getweather())

    if light != None:
        if int(light) < 500:
            lightFlag = "Put plant in sunlight"
        else:
            lightFlag = "No need to put plant in sunlight"
    else:
        lightFlag = "No need to put plant in sunlight"

    if soilMoisture != None:
        if int(soilMoisture) < 20:
            waterFlag = "Time to water plant"
        elif int(soilMoisture) > 60:
            waterFlag = "Stop watering plant"
        else:
            waterFlag = "Good moisture level for plant"
    else:
        waterFlag = "Good moisture level for plant"

    if temp != None:
        if float(temp) < 60.0:
            tempFlag = "Put plant in a warmer place"
        elif float(temp) > 85.0:
            tempFlag = "Put plant in a cooler place"
        else:
            tempFlag = "Good temperature for plant"
    else:
        tempFlag = "Good temperature for plant"

    return render_template("index.html", light=light, soilMoisture=soilMoisture, temp=temp, humid=humid, 
                            day=day, time=time,  weatherText=weatherText, weatherTemp=weatherTemp, 
                            weather1Day=weather1Day, weather2Day=weather2Day, lightFlag=lightFlag, 
                            waterFlag=waterFlag, tempFlag=tempFlag, avgTemp=avgTemp, today=today)


# @app.route("/")
# # @app.route("/<uv>&<soilMoisture>")
# def index(uv = None, soilMoisture = None, temp = None, humid = None):
#     uv = request.args.get("uv")
#     soilMoisture = request.args.get("soilMoisture")
#     temp = request.args.get("temp")
#     humid = request.args.get("humid")

#     print("1111111")

#     with open("sensorData.txt", 'a+') as file:
#         print("In here!")
#         file.write("UV: " + str(uv) + " Soil Moisture: " + str(soilMoisture) + " Temperature: " + str(temp) + " Humidity: "+ str(humid) +"\n")

#     print("UV: " + str(uv))
#     print("Soil Moisture: " + str(soilMoisture))
#     print("Temperature: " + str(temp))
#     print("Humidity: " + str(humid))

#     showUV = 0
#     showSoil = 0
#     showTemp = 0
#     showHumid = 0

#     with open("sensorData.txt", 'r') as file:
#         for lastLine in file:
#             pass
#         showUV = lastLine.split()[1]
#         showSoil = lastLine.split()[4]
#         showTemp = lastLine.split()[6]
#         showHumid = lastLine.split()[8]

#     return render_template("index.html", uv=showUV, soilMoisture=showSoil, temp = showTemp, humid = showHumid)
