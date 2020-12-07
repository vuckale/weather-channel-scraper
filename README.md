# The Weather Channel Scraper
A python script that scrapes weather related data from [weather.com](https://weather.com/) with the help of `bs4`
## How to run

### Environment

Runs on Python `3.*`. Check your Python version with:
```
python3 --version
```

You would also need `pip3` for installing `bs4`

Install `pip3`:
```
sudo apt-get -y install python3-pip
```

### Setup

Clone repository:
```
git clone https://github.com/vuckale/weather-channel-scraper.git
```

Navigate to cloned repository and:

```
pip3 -r requirements.txt
```

### Usage

```
Usage: weather_channel.py [options]

Options:
  -h, --help            show this help message and exit
  -v, --verbose         print verbose output
  -c, --current         print current weather temperature in set location
  -u URL, --url=URL     use this url to fetch weather data
  --one-line=ONE_LINE   print everything on one line (put delimiter inside of
                        "quotes" in place of ONE_LINE)
  -d, --details         print details for current weather
  --d-feels-like        print high/low for today
  --d-sunrise-sunset    print sunrise/sunset time for today
  --d-high-low          print high/low for today
  --d-wind              print wind speed for today
  --d-humidity          print humidity for today
  --d-dew-point         print dew-point for today
  --d-pressure          print pressure for today
  --d-uw-index          print uw-index for today
  --d-visibility        print visibility range for today
  --d-moon-phase        print moon-phase for today
  --sun-position        print a graphical representation of current sun
                        position
  --location            print a location
  --day-light-duration  print how long does day light last
  --day-light-left      print how long is left before day light ends
  --current-timestamp   print timestamp when current temperature was measured
  --air-quality         print air quality index
```
Set a url inside of `url` variable or pass it as argument of `-u` option

Url has to match a `https://weather.com/en-GB/weather/today/l/*` i.e. visit [https://weather.com/en-GB/](https://weather.com/en-GB/), type in your city in search bar and copy that url.

Example for `Los Angeles, CA, United States`

```python
url = "https://weather.com/en-GB/weather/today/l/a4bf563aa6c1d3b3daffff43f51e3d7f765f43968cddc0475b9f340601b8cc26"
```
you can then run following command to get current temperature:
```
./weather_channel.py -v -c
```

or 

```
./weather_channel.py -v -c --url="https://weather.com/en-GB/weather/today/l/a4bf563aa6c1d3b3daffff43f51e3d7f765f43968cddc0475b9f340601b8cc26"
```
this will return current temperature in Los Angeles as of `2020-12-07 21:26 CET` in `°C` with verbose output:
```
Current: Sunny 18°
```
### Using Weather Icons
<p align="center">
  <img src="https://https://github.com/vuckale/weather-channel-scraper/blob/master/screenshot1.png?raw=true" />
</p>

Navigate to the cloned repository and run:

```
git submodule init 
```

```
git submodule update
```

to pull [weather-icons](https://github.com/erikflowers/weather-icons.git) repository or clone it directly with:

```
git clone https://github.com/erikflowers/weather-icons.git
```

Install fonts with:

```
cd weather-icons
mv font/weathericons-regular-webfont.ttf /usr/share/fonts/truetype
fc-cache -vf
```

Check if font is correctly installed with:

```fc-list | grep "Weather Icons"```

if you get a line that looks somewhat like this it was successfully installed:

```
~/.local/share/fonts/weathericons-regular-webfont.ttf: Weather Icons:style=Regular
```
