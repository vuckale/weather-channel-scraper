#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import datetime
from getopt import getopt
import sys
from optparse import OptionParser
import optparse

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
	usage = "usage: %prog [options] arg1 arg2"
	parser = OptionParser(usage=usage)
	parser.add_option("-c", "--current",
                  action="store_true", dest="current",
                  help="print current weather temperature in set location")
	(options, args) = parser.parse_args()

	count_None = 0
	for key, value in options.__dict__.items():
		if value != None:
			continue
		else:
			count_None += 1

	if count_None == len(options.__dict__.items()):
		print('ERROR: at least one option should be provided')
		sys.exit()

	global 	current_dateTime, sunset_dateTime, sunrise_dateTime
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
		except OSError as e:
			pass
		if options.current:
			print(getIcon(weather_condition) + ' ' + temperature + 'C')


if __name__ == "__main__":
    main()
