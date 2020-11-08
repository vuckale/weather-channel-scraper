#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import datetime
from getopt import getopt
import sys
from optparse import OptionParser, OptionValueError
import optparse

# global variables
url = ""
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
	global current_dateTime, sunset_dateTime, sunrise_dateTime

	sunset_sunrise = ""
	if current_dateTime > sunset_dateTime.replace(minute=(sunset_dateTime.minute - 20)) and current_dateTime <= sunset_dateTime:
		sunset_sunrise = "  "
	elif current_dateTime > sunrise_dateTime.replace(minute=(sunrise_dateTime.minute - 20)) and current_dateTime <= sunrise_dateTime:
		sunset_sunrise = "  "

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

	return options[weather_condition] + sunset_sunrise


details_dict = {
	"--d-high-low" : False,
	"--d-feels-like" : False,
	"--d-wind" : False,
	"--d-humidity" : False,
	"--d-dew-point" : False,
	"--d-pressure" : False,
	"--d-uw-index" : False,
	"--d-visibility" : False,
	"--d-moon-phase" : False
}


def check_options(option, opt_str, value, parser):
	if parser.values.details:
		print("ERROR: either option -d, --details alone or multiple --d-* options can be passed")
		sys.exit()

	details_dict[opt_str] = True


def iterate_details(details, index):
	if index >= 0:
		detail = details[index]
		label = detail.select('div[data-testid^=WeatherDetailsLabel]')
		data = detail.select('div[data-testid^=wxData]')
		return [label[0].text, data[0].text]
	elif index == -1:
		# for scraping feels like section
		feels_like = details.select('div[data-testid^=FeelsLikeSection]')[0]
		label = feels_like.select('span[data-testid^=FeelsLikeLabel]')
		data = feels_like.select('span[data-testid^=TemperatureValue]')
		return [label[0].text, data[0].text]


def main():
	usage = "usage: %prog [options] arg1 arg2"
	parser = OptionParser(usage=usage)
	parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose",
                  help="print verbose output")
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
	parser.add_option("--one-line",
                  action="store_true", dest="one_line",
                  help="print everything on one line")
	parser.add_option("--d-feels-like",
                  action="callback", callback=check_options,
                  help="print high/low for today")
	parser.add_option("--d-high-low",
                  action="callback", callback=check_options,
                  help="print high/low for today")
	parser.add_option("--d-wind",
                  action="callback", callback=check_options,
                  help="print wind speed for today")
	parser.add_option("--d-humidity",
                  action="callback", callback=check_options,
                  help="print humidity for today")
	parser.add_option("--d-dew-point",
                  action="callback", callback=check_options,
                  help="print dew-point for today")
	parser.add_option("--d-pressure",
                  action="callback", callback=check_options,
                  help="print pressure for today")
	parser.add_option("--d-uw-index",
                  action="callback", callback=check_options,
                  help="print uw-index for today")
	parser.add_option("--d-visibility",
                  action="callback", callback=check_options,
                  help="print visibility range for today")
	parser.add_option("--d-moon-phase",
                  action="callback", callback=check_options,
                  help="print moon-phase for today")

	(options, args) = parser.parse_args()

	if options.details:
		for key, value in details_dict.items():
				if value:
					print("ERROR: either option -d, --details alone or multiple --d-* options can be passed")
					sys.exit()

	count_None = 0
	for key, value in options.__dict__.items():
		if value != None and key != 'url':
			continue
		else:
			count_None += 1

	if count_None == len(options.__dict__.items()) and not details_dict:
		parser.print_help()
		sys.exit()

	printing_style = ' ' if options.one_line else '\n'

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
			print(getIcon(weather_condition) + " " + temperature + 'C', end = printing_style)
		if options.sunrise_sunset:
			print('sunrise at: ' + str(sunrise_dateTime.hour) + ':' + str(sunrise_dateTime.minute) + ' | ' +'sunset at: ' + str(sunset_dateTime.hour) + ':' + str(sunset_dateTime.minute), end = printing_style)

		details = soup.select('section[data-testid^=TodaysDetailsModule]')[0]

		if details_dict["--d-feels-like"]:
			feels_like = iterate_details(details, -1)
			print(feels_like[0] + ': ' + feels_like[1] if options.verbose else feels_like[1], end = printing_style)

		other_details_list = details.select('div[data-testid^=WeatherDetailsListItem]')

		if details_dict["--d-high-low"]:
			high_low = iterate_details(other_details_list, 0)
			print(high_low[0] + ': ' + high_low[1] if options.verbose else high_low[1], end = printing_style)

		if details_dict["--d-wind"]:
			wind = iterate_details(other_details_list, 1)
			print(wind[0] + ': ' + wind[1] if options.verbose else wind[1], end = printing_style)

		if details_dict["--d-humidity"]:
			humidity = iterate_details(other_details_list, 2)
			print(humidity[0] + ': ' + humidity[1] if options.verbose else humidity[1], end = printing_style)

		if details_dict["--d-dew-point"]:
			dew_point = iterate_details(other_details_list, 3)
			print(dew_point[0] + ': ' + dew_point[1] if options.verbose else dew_point[1], end = printing_style)

		if details_dict["--d-pressure"]:
			pressure = iterate_details(other_details_list, 4)
			print(pressure[0] + ': ' + pressure[1] if options.verbose else pressure[1], end = printing_style)

		if details_dict["--d-uw-index"]:
			uw_index = iterate_details(other_details_list, 5)
			print(uw_index[0] + ': ' + uw_index[1] if options.verbose else uw_index[1], end = printing_style)

		if details_dict["--d-visibility"]:
			visibility = iterate_details(other_details_list, 6)
			print(visibility[0] + ': ' + visibility[1] if options.verbose else visibility[1], end = printing_style)

		if details_dict["--d-moon-phase"]:
			moon_phase = iterate_details(other_details_list, 7)
			print(moon_phase[0] + ': ' + moon_phase[1] if options.verbose else moon_phase[1], end = printing_style)

		if options.details:
			feels_like = iterate_details(details, -1)
			print(feels_like[0] + ': ' + feels_like[1] if options.verbose else feels_like[1], end = printing_style)
			for i in range (0, len(other_details_list)):
				detail = iterate_details(other_details_list, i)
				print(detail[0] + ': ' + detail[1] if options.verbose else detail[1], end = printing_style)


if __name__ == "__main__":
    main()
