#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import datetime
from getopt import getopt
import sys

# global variables
url = ""
current_dateTime = None
sunset_dateTime = None
sunrise_dateTime = None


def sunIsUp():
	global current_dateTime, sunset_dateTime, sunrise_dateTime
	if (current_dateTime <= sunset_dateTime and current_dateTime >= sunrise_dateTime):
		return True
	else:
		return False


def getIcon(weather_condition):
	options = {
		'Sunny' : '',
		'Mostly Sunny' : '',
		'Partly Sunny' : '',
		
		'Cloudy' : '',
		'Partly Cloudy' : '' if sunIsUp() else '󰼱',
		'Mostly Cloudy' : '',
		
		'Fair' : '' if sunIsUp() else '󰼱',
		'Clear' : '' if sunIsUp() else '󰖔',
		'Fog' : '󰖑',
		'Showers' : '',
		'T-Storms' : '',
		'Rain' : '',
		'Snow' : '',
		'Windy':'' 
	}
	return options[weather_condition]


def main():
	try:
		opts, args = getopt(sys.argv[1:], "cho:v", ["current", "help", "output="])
	except getopt.GetoptError as err:
		print(err)
		sys.exit(2)

	output = None
	verbose = False
	current_flag = False
	for o, a in opts:
		if o in ("-c", "--current"):
			current_flag = True
		elif o == "-v":
			print("option -v")
			verbose = True
		elif o in ("-h", "--help"):
			print("option -h, --help")
			sys.exit()
		elif o in ("-o", "--output"):
			print("option -o, --output")
			output = a
		else:
			assert False, "unhandled option"

	global 	current_dateTime, sunset_dateTime, sunrise_dateTime
	if (current_flag):
		if not url:
			print('url not specified: visit https://weather.com/en-GB/, enter your destination and pate url in \'url\' variable')
		else:
				try:
					html_doc = requests.get(url).text
					soup = BeautifulSoup(html_doc, 'html.parser')
					sunrise_sunset = soup.find("div", {"class" : "SunriseSunset--datesContainer--3YG_Q"})
					sunrise = sunrise_sunset.find("div" , {"data-testid" : "SunriseValue"}).p.string
					sunset = sunrise_sunset.find("div" , {"data-testid" : "SunsetValue"}).p.string
					sunrise_split = sunrise.split(':')
					sunrise_dateTime = (datetime.datetime.now()).replace(hour=int(sunrise_split[0]), minute=int(sunrise_split[1]))
					sunset_split = sunset.split(':')
					sunset_dateTime = (datetime.datetime.now()).replace(hour=int(sunset_split[0]), minute=(int(sunset_split[1])))
					current_dateTime = datetime.datetime.now()
					currentWeather = soup.find("div", { "class" : "CurrentConditions--primary--3xWnK" })
					temperature = currentWeather.span.string
					weather_condition = currentWeather.div.string
					print( getIcon(weather_condition) + ' ' + temperature + 'C')
				except OSError as e:
					pass


if __name__ == "__main__":
    main()
