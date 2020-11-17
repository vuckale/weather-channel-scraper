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
		'T-Storms' : '',
		'Rain' : '',
		'Snow' : '',
		'Windy':''
	}

	if weather_condition in conditions:
		return weather_condition + ' ' + sunset_sunrise if options.verbose\
			 else conditions[weather_condition] + sunset_sunrise
	else:
		return weather_condition + ' ' + sunset_sunrise


details_dict = {
	"--d-feels-like" : False,
	"--d-sunrise-sunset" : False,
	"--d-high-low" : False,
	"--d-wind" : False,
	"--d-humidity" : False,
	"--d-dew-point" : False,
	"--d-pressure" : False,
	"--d-uw-index" : False,
	"--d-visibility" : False,
	"--d-moon-phase" : False
}

icons = {
	"--current" : ' ',
	"--d-feels-like" : '󰙍 ',
	"--d-sunrise-sunset" : '󰖜󰖛 ',
	"--d-high-low" : ' ',
	"--d-wind" : ' ',
	"--d-humidity" : ' ',
	"--d-dew-point" : ' ',
	"--d-pressure" : ' ',
	"--d-uw-index" : '󰖙 ',
	"--d-visibility" : '󰈈 ',
	"--d-moon-phase" : '󰽥 '
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
	elif index == -2:
		# for scraping sunset/sunrise
		sunrise_sunset = details.select('div[data-testid^=sunriseSunsetContainer]')[0]
		sunrise_data = sunrise_sunset.select('div[data-testid^=SunriseValue]')[0].p.text
		sunset_data = sunrise_sunset.select('div[data-testid^=SunsetValue]')[0].p.text
		return sunrise_data + '/' + sunset_data


def draw_sun_position():
	global current_dateTime, sunset_dateTime, sunrise_dateTime
	if sunIsUp():
		diff = sunset_dateTime - sunrise_dateTime
		step = diff.seconds/10
		current_diff = sunset_dateTime - current_dateTime
		current_diff_step = current_diff/step
		sun_pos = abs(round(current_diff_step.seconds) - 10)
		output = ""
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

	if count_None == len(options.__dict__.items()) and not any(details_dict.values()):
		parser.print_help()
		sys.exit()

	if options.one_line:
		if len(options.one_line) > 1:
			print("ERROR: " + options.one_line + " is invalid --one-line argument, it is a character that will be used as a delimiter. It can't contain more than 1 character.")
			print("Maybe you forgot to put it and placed another option instead?")
			sys.exit()

	if options.one_line and count_None == len(options.__dict__.items()) - 1:
		print("ERROR: --one-line option alone doesn't have anything to print")
		sys.exit()

	printing_style = ' ' + str(options.one_line) + ' ' if options.one_line else '\n'

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

			# converting sunrise/sunset into datetime
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

			if options.current:
				output +=  'Current: ' + getIcon(weather_condition) + temperature + printing_style if options.verbose else ' ' + getIcon(weather_condition) + " " + temperature + 'C' + printing_style

			if any(details_dict.values()) or options.details:
				details = soup.select('section[data-testid^=TodaysDetailsModule]')[0]
				other_details_list = details.select('div[data-testid^=WeatherDetailsListItem]')

			if details_dict["--d-feels-like"]:
				feels_like = iterate_details(details, -1)
				output += feels_like[0] + ': ' + feels_like[1] + printing_style if options.verbose else icons['--d-feels-like'] + feels_like[1] + printing_style

			if details_dict["--d-sunrise-sunset"]:
				sunrise_sunset = iterate_details(details, -2)
				output += 'sunrise/sunset: ' + sunrise_sunset+ printing_style if options.verbose else icons['--d-sunrise-sunset'] + sunrise_sunset + printing_style

			if details_dict["--d-high-low"]:
				high_low = iterate_details(other_details_list, 0)
				output += high_low[0] + ': ' + high_low[1] + printing_style if options.verbose else icons['--d-high-low'] + high_low[1] + printing_style

			if details_dict["--d-wind"]:
				wind = iterate_details(other_details_list, 1)
				output += wind[0] + ': ' + wind[1] + printing_style if options.verbose else icons['--d-wind'] +  wind[1] + printing_style

			if details_dict["--d-humidity"]:
				humidity = iterate_details(other_details_list, 2)
				output += humidity[0] + ': ' + humidity[1] + printing_style if options.verbose else icons['--d-humidity'] + humidity[1] + printing_style

			if details_dict["--d-dew-point"]:
				dew_point = iterate_details(other_details_list, 3)
				output += dew_point[0] + ': ' + dew_point[1] + printing_style if options.verbose else icons['--d-dew-point'] + dew_point[1] + printing_style

			if details_dict["--d-pressure"]:
				pressure = iterate_details(other_details_list, 4)
				output += pressure[0] + ': ' + pressure[1] + printing_style if options.verbose else icons['--d-pressure'] + pressure[1] + printing_style

			if details_dict["--d-uw-index"]:
				uw_index = iterate_details(other_details_list, 5)
				output += uw_index[0] + ': ' + uw_index[1] + printing_style if options.verbose else icons['--d-uw-index'] + uw_index[1] + printing_style

			if details_dict["--d-visibility"]:
				visibility = iterate_details(other_details_list, 6)
				output += visibility[0] + ': ' + visibility[1] + printing_style if options.verbose else icons['--d-visibility'] + visibility[1] + printing_style

			if details_dict["--d-moon-phase"]:
				moon_phase = iterate_details(other_details_list, 7)
				output += moon_phase[0] + ': ' + moon_phase[1] + printing_style if options.verbose else icons['--d-moon-phase'] + moon_phase[1] + printing_style

			if options.details:
				feels_like = iterate_details(details, -1)
				output += feels_like[0] + ': ' + feels_like[1] + printing_style if options.verbose else icons['--d-feels-like'] + feels_like[1] + printing_style
				sunrise_sunset = iterate_details(details, -2)
				output += 'sunrise/sunset: ' + sunrise_sunset+ printing_style if options.verbose else icons['--d-sunrise-sunset'] + sunrise_sunset + printing_style
				icons_list = list(icons.values())
				for i in range (0, len(other_details_list)):
					detail = iterate_details(other_details_list, i)
					output += detail[0] + ': ' + detail[1] + printing_style if options.verbose else icons_list[i + 3] + detail[1] + printing_style

			if options.sun_position and sunIsUp():
				output += draw_sun_position() + printing_style

			if options.one_line:
				print(output[:-3])
			else:
				print(output[:-1])
		except Exception as e:
			print("X")

if __name__ == "__main__":
    main()
