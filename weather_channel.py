#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import datetime
from getopt import getopt
import sys
import os
from optparse import OptionParser, OptionValueError
import optparse
import re

# global variables
url = ""

current_dateTime = None
sunset_dateTime = None
sunrise_dateTime = None
day_light = None
day_light_left = None
soup = None
options = None


def sunIsUp():
	global current_dateTime, sunset_dateTime, sunrise_dateTime
	if (current_dateTime <= sunset_dateTime and current_dateTime >= sunrise_dateTime):
		return True
	else:
		return False


def getIcon(weather_condition):
	global current_dateTime, sunset_dateTime, sunrise_dateTime
	timedelta = datetime.timedelta(minutes=20)
	sunset_sunrise = ""
	if current_dateTime > sunset_dateTime - timedelta and current_dateTime <= sunset_dateTime:
		sunset_sunrise = "  "
	elif current_dateTime > sunrise_dateTime - timedelta and current_dateTime <= sunrise_dateTime:
		sunset_sunrise = "  "

	conditions = {
		'Sunny' : '',
		'Mostly Sunny' : '',
		'Partly Sunny' : '',

		'Cloudy' : '',
		'Partly Cloudy' : '' if sunIsUp() else '󰼱',
		'Mostly Cloudy' : '',

		'Fair' : '' if sunIsUp() else '󰼱',
		'Clear' : '' if sunIsUp() else '󰖔',
		'Fog' : '󰖑',
		'Rain Shower' : '',
		'Showers in the Vicinity' : '',
		'T-Storms' : '',
		'Rain' : '',
		'Rain and Snow' : '󰜗',
		'Light Snow' : '',
		'Light Freezing Rain' : '',
		'Snow' : '',
		'Snow Shower' : '',
		'Freezing Drizzle' : '󰜗',
		'Windy':'',
		'Thunderstorm': '󰙾',
		'Light Rain with Thunder': '󰙾',
		# Light Rain/Freezing Rain
		# Rain/Freezing Rain
		# Wintry Mix
		# Drizzle
	    # Heavy Rain
		'Light Rain': ''
	}

	if weather_condition in conditions:
		return weather_condition + '' + sunset_sunrise if options.verbose\
			 else conditions[weather_condition] + sunset_sunrise
	else:
		return weather_condition + '' + sunset_sunrise


details_dict = {
	"--d-feels-like" : (False, -1),
	"--d-sunrise-sunset" : (False, -2),
	"--d-high-low" : (False, 0),
	"--d-wind" : (False, 1),
	"--d-humidity" : (False, 2),
	"--d-dew-point" : (False, 3),
	"--d-pressure" : (False, 4),
	"--d-uw-index" : (False, 5),
	"--d-visibility" : (False, 6),
	"--d-moon-phase" : (False, 7)
}


weather_icons = {
	"--d-feels-like" : '󰙍 ',
	"--d-sunrise-sunset" : '󰖜󰖛 ',
	"--d-high-low" : '  ',
	"--d-wind" : '  ',
	"--d-humidity" : '  ',
	#"--d-humidity" : '',
	"--d-dew-point" : '  ',
	"--d-pressure" : '  ',
	"--d-uw-index" : ' 󰖙 ',
	"--d-visibility" : ' 󰈈 ',
	"--d-moon-phase" : ' 󰽥 '
}


misc_icons = {
	"arrow-down" : ' 󰁅 ',
	"arrow-up" : ' 󰁝 ',
	"air-quality" : ' 󰌪 '
}


def check_options(option, opt_str, value, parser):
	if parser.values.details:
		print("ERROR: either option -d, --details alone or multiple --d-* options can be passed")
		sys.exit()
	details_dict[opt_str] = (True, details_dict[opt_str][1])


def url_usage():
	print('visit https://weather.com/en-GB/, enter your destination and paste url in \'url\' variable')


def parse_details(details, index):
	if index >= 0:
		detail = details[index]
		label = detail.select('div[data-testid^=WeatherDetailsLabel]')
		data = detail.select('div[data-testid^=wxData]')
		if detail.svg['name'] == 'pressure':
			parse_pressure = re.findall("\d+\.\d+", data[0].text)
			svg = data[0].svg
			if svg != None:
				return [label[0].text, misc_icons[svg['name']] + parse_pressure[0] + " mb"]
		if detail.svg['name'] == 'wind':
			parse_wind = re.sub(r"\D", "", data[0].text)
			mph_to_kmh = int(parse_wind) * 1.609
			return [label[0].text, str(round(mph_to_kmh, 2)) + " kmh"]
		return [label[0].text, data[0].text]
	elif index == -1:
		# for scraping feels like section
		feels_like = details.select('div[data-testid^=FeelsLikeSection]')[0]
		label = feels_like.select('span[data-testid^=FeelsLikeLabel]')
		data = feels_like.select('span[data-testid^=TemperatureValue]')
		return [label[0].text, data[0].text]
	elif index == -2:
		# for scraping sunset/sunrise
		sunrise_sunset = details.select('div[data-testid^=sunriseSunsetContainer]')[0]
		sunrise_data = sunrise_sunset.select('div[data-testid^=SunriseValue]')[0].p.text
		sunset_data = sunrise_sunset.select('div[data-testid^=SunsetValue]')[0].p.text
		return ["sunrise/sunset", sunrise_data + '/' + sunset_data]


def draw_sun_position():
	global day_light, current_dateTime, sunset_dateTime, sunrise_dateTime
	if sunIsUp():
		step = day_light.seconds/10
		day_light_left_step = day_light_left/step
		sun_pos = abs(round(day_light_left_step.seconds) - 10)
		output = " "
		for i in range(0, 11):
			if i == sun_pos:
				output += ''
			else:
				output += '-'
		return output

def main():
	global options
	output = ""
	usage = "usage: %prog [options]"
	parser = OptionParser(usage=usage)
	parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose",
                  help="print verbose output")
	parser.add_option("-c", "--current",
                  action="store_true", dest="current",
                  help="print current weather temperature in set location")
	parser.add_option("-u", "--url",
                  action="store", dest="url",
                  help="use this url to fetch weather data")
	parser.add_option("--one-line", action="store", dest="one_line",
                  help="print everything on one line (put delimiter inside of \"quotes\" in place of ONE_LINE)")
	parser.add_option("-d", "--details",
                  action="store_true", dest="details",
                  help="print details for current weather")
	parser.add_option("--d-feels-like",
                  action="callback", callback=check_options,
                  help="print high/low for today")
	parser.add_option("--d-sunrise-sunset",
                  action="callback", callback=check_options,
                  help="print sunrise/sunset time for today")
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
	parser.add_option("--sun-position",
                  action="store_true", dest="sun_position",
                  help="print a graphical representation of current sun position")
	parser.add_option("--location",
                  action="store_true", dest="location",
                  help="print a location")
	parser.add_option("--day-light-duration",
                  action="store_true", dest="day_light_duration",
                  help="print how long does day light last")
	parser.add_option("--day-light-left",
                  action="store_true", dest="day_light_left",
                  help="print how long is left before day light ends")
	parser.add_option("--current-timestamp",
                  action="store_true", dest="current_timestamp",
                  help="print timestamp when current temperature was measured")
	parser.add_option("--air-quality",
                  action="store_true", dest="air_quality",
                  help="print air quality index")

	(options, args) = parser.parse_args()

	# parse detail_options i.e --d-*
	detail_options = []
	for i in range (1, len(sys.argv)):
		if str(sys.argv[i]) in details_dict.keys():
			detail_options.append((sys.argv[i], details_dict[sys.argv[i]][1]))

	# count the number of options passed
	# OptionParser returns a dictionary with None or True assigned to each option
	# option "-url" is not counted since it does not generate any output
	count_None = 0
	for key, value in options.__dict__.items():
		if value != None and key != 'url':
			continue
		else:
			count_None += 1

	# if every option counted is None then 0 options are passed
	# detail options are considered separately
	if count_None == len(options.__dict__.items()) and len(detail_options) == 0:
		parser.print_help()
		sys.exit()

	if options.current_timestamp and not options.current:
		print("ERROR: option \"--current-timestamp\" can't be passed without option \"current\"")
		sys.exit()

	# if options.one_line:
	# 	if len(options.one_line) > 1:
	# 		print("ERROR: " + options.one_line + " is invalid --one-line argument, it is a character that will be used as a delimiter. It can't contain more than 1 character.")
	# 		print("Maybe you forgot to put it and placed another option instead?")
	# 		sys.exit()

	if options.one_line and count_None == len(options.__dict__.items()) - 1:
		print("ERROR: --one-line option alone doesn't have anything to print")
		sys.exit()

	printing_style = "" + str(options.one_line) + "" if options.one_line else '\n'

	global current_dateTime, sunset_dateTime, sunrise_dateTime, url, soup, day_light, day_light_left

	if options.url:
		url = options.url
	if not url:
		print('ERROR: url not specified: ', end='')
		url_usage()
		sys.exit()
	elif not url.startswith('https://weather.com/en-GB/weather/today/l/'):
		print('ERROR: url has to have a form: https://weather.com/en-GB/weather/today/l/')
		url_usage()
		sys.exit()
	else:
		try:
			if url:
				html_doc = requests.get(url).text
			else:
				html_doc = requests.get(options.url).text
			soup = BeautifulSoup(html_doc, 'html.parser')
			# converting sunrise/sunset into datetime
			sunrise_sunset = soup.find('div', id = re.compile("SunriseSunsetContainer.*"))
			sunrise = sunrise_sunset.find("div" , {"data-testid" : "SunriseValue"}).p.string
			sunset = sunrise_sunset.find("div" , {"data-testid" : "SunsetValue"}).p.string
			sunrise_split = sunrise.split(':')
			sunrise_dateTime = (datetime.datetime.now()).replace(hour=int(sunrise_split[0]), minute=int(sunrise_split[1]))
			sunset_split = sunset.split(':')
			sunset_dateTime = (datetime.datetime.now()).replace(hour=int(sunset_split[0]), minute=(int(sunset_split[1])))
			current_dateTime = datetime.datetime.now()

			if options.current or options.location:
				current_section = soup.find('div', id = re.compile("WxuCurrentConditions-main-.*"))

			if options.current_timestamp:
				timestamp = current_section.find("span", {"class" : re.compile("CurrentConditions--timestamp--.*")}).text

			if options.location:
				location = current_section.find("h1", {"class" : re.compile("CurrentConditions--location--.*")}).text
				output += location + printing_style

			if options.current:
				currentWeather = current_section.find("div", { "class" : re.compile("CurrentConditions--primary--.*") })
				temperature = currentWeather.span.text
				weather_condition = currentWeather.div.string
				output +=  'Current: ' + getIcon(weather_condition) + temperature + \
				 (' ' + timestamp if options.current_timestamp else '') + \
				 printing_style if options.verbose else getIcon(weather_condition) + " " + temperature + \
				 (' ' + timestamp if options.current_timestamp else '') + printing_style

			if any(details_dict.values()) or options.details:
				details = soup.select('section[data-testid^=TodaysDetailsModule]')[0]
				other_details_list = details.select('div[data-testid^=WeatherDetailsListItem]')
			for i in detail_options:
				if i[1] >= 0:
					x = other_details_list
				else:
					x = details
				a = parse_details(x, int(i[1]))
				output += a[0] + ': ' + a[1] + printing_style if options.verbose else weather_icons[i[0]] + a[1] + printing_style

			if options.details:
				feels_like = parse_details(details, -1)
				output += feels_like[0] + ': ' + feels_like[1] + printing_style if options.verbose else weather_icons['--d-feels-like'] + feels_like[1] + printing_style
				sunrise_sunset = parse_details(details, -2)
				output += 'sunrise/sunset: ' + sunrise_sunset[1] + printing_style if options.verbose else weather_icons['--d-sunrise-sunset'] + sunrise_sunset[1] + printing_style
				icons_list = list(weather_icons.values())
				for i in range (0, len(other_details_list)):
					detail = parse_details(other_details_list, i)
					output += detail[0] + ': ' + detail[1] + printing_style if options.verbose else icons_list[i + 2] + detail[1] + printing_style

			if sunIsUp():
				if options.sun_position or options.day_light_duration or options.day_light_left:
					day_light = sunset_dateTime -sunrise_dateTime
					day_light_left = sunset_dateTime - current_dateTime

				if options.day_light_duration:
					day_light_delta = str(day_light).split(':')
					day_light_string = day_light_delta[0] + 'h ' + day_light_delta[1] + 'm' + printing_style
					output += 'Day light duration: ' + day_light_string if options.verbose else day_light_string

				if options.day_light_left:
					day_light_left_delta = str(day_light_left).split(':')
					day_light_left_string = day_light_left_delta[0] + 'h ' + day_light_left_delta[1] + 'm' + printing_style
					output += 'Day light left: ' + day_light_left_string if options.verbose else day_light_left_string

				if options.sun_position:
					output += draw_sun_position() + printing_style

			if options.air_quality:
				air_quality_section = soup.select("section[title^='Air Quality Index']")[0]
				label = air_quality_section.select("header[data-testid^=HeaderTitle]")[0].text
				value = air_quality_section.select("text[data-testid^=DonutChartValue]")[0].text
				output += label + ": " + value + printing_style if options.verbose else misc_icons["air-quality"] + value + printing_style

			if options.one_line:
				print(output[:-11])
			else:
				print(output[:-1])
		except Exception as e:
			if e.__class__ == requests.exceptions.ConnectionError:
				print(os.path.basename(__file__) + ": no internet connection")
			else:
				raise e

if __name__ == "__main__":
    main()
