#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import datetime
from getopt import getopt
import sys
from optparse import OptionParser
import optparse

# global variables
url=""
current_dateTime = None
sunset_dateTime = None
sunrise_dateTime = None
soup = None

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
	parser.add_option("-s", "--sunrise-sunset",
                  action="store_true", dest="sunrise_sunset",
                  help="print datetime for sunrise and sunset in set location")
	parser.add_option("-u", "--url",
                  action="store", dest="url",
                  help="use this url to fetch weather data")
	parser.add_option("-d", "--details",
                  action="store_true", dest="details",
                  help="print details for current weather")
	(options, args) = parser.parse_args()

	count_None = 0
	for key, value in options.__dict__.items():
		if value != None and key != 'url':
			continue
		else:
			count_None += 1

	if count_None == len(options.__dict__.items()):
		parser.print_help()
		sys.exit()

	global 	current_dateTime, sunset_dateTime, sunrise_dateTime, url, soup
	if not url and (not options.url):
			print('url not specified: visit https://weather.com/en-GB/, enter your destination and pate url in \'url\' variable')
	else:
		try:
			if url:
				html_doc = requests.get(url).text
			else:
				html_doc = requests.get(options.url).text
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
		if options.sunrise_sunset:
			print('sunrise at: ' + str(sunrise_dateTime.hour) + ':' + str(sunrise_dateTime.minute) + ' | ' +'sunset at: ' + str(sunset_dateTime.hour) + ':' + str(sunset_dateTime.minute))
		if options.details:
			details = soup.select('section[data-testid^=TodaysDetailsModule]')[0]
			feels_like = details.select('div[data-testid^=FeelsLikeSection]')[0]
			feels_like_label = feels_like.select('span[data-testid^=FeelsLikeLabel]')[0].text
			feels_like_temp = feels_like.select('span[data-testid^=TemperatureValue]')[0].text
			print(feels_like_label + ' -> ' + feels_like_temp)
			other_details_list = details.select('div[data-testid^=WeatherDetailsListItem]')
			high_low = other_details_list[0]
			high_low_label = high_low.select('div[data-testid^=WeatherDetailsLabel]')
			high_low_data = high_low.select('div[data-testid^=wxData]')
			print(high_low_label[0].text + ' -> ' + high_low_data[0].text)
			wind = other_details_list[1]
			wind_label = wind.select('div[data-testid^=WeatherDetailsLabel]')
			wind_data = wind.select('div[data-testid^=wxData]')
			print(wind_label[0].text + ' -> ' + wind_data[0].text)
			humidity = other_details_list[2]
			humidity_label = humidity.select('div[data-testid^=WeatherDetailsLabel]')
			humidity_data = humidity.select('div[data-testid^=wxData]')
			print(humidity_label[0].text + ' -> ' + humidity_data[0].text)
			dew_point = other_details_list[3]
			dew_point_label = dew_point.select('div[data-testid^=WeatherDetailsLabel]')
			dew_point_data = dew_point.select('div[data-testid^=wxData]')
			print(dew_point_label[0].text + ' -> ' + dew_point_data[0].text)
			pressure = other_details_list[4]
			pressure_label = pressure.select('div[data-testid^=WeatherDetailsLabel]')
			pressure_data = pressure.select('div[data-testid^=wxData]')
			print(pressure_label[0].text + ' -> ' + pressure_data[0].text)
			uv_index = other_details_list[5]
			uv_index_label = uv_index.select('div[data-testid^=WeatherDetailsLabel]')
			uv_index_data = uv_index.select('div[data-testid^=wxData]')
			print(uv_index_label[0].text + ' -> ' + uv_index_data[0].text)
			visibility = other_details_list[6]
			visibility_label = visibility.select('div[data-testid^=WeatherDetailsLabel]')
			visibility_data = visibility.select('div[data-testid^=wxData]')
			print(visibility_label[0].text + ' -> ' + visibility_data[0].text)
			moon_phase = other_details_list[7]
			moon_phase_label = moon_phase.select('div[data-testid^=WeatherDetailsLabel]')
			moon_phase_data = moon_phase.select('div[data-testid^=wxData]')
			print(moon_phase_label[0].text + ' -> ' + moon_phase_data[0].text)


if __name__ == "__main__":
    main()
