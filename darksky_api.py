# -*- coding: utf-8 -*-
from flask import Flask, abort, Blueprint, jsonify, make_response
from flask_cors import CORS
from flask_graylog_local import Graylog
from location_class import DarkSky
from geonames_parser import Geonames
from geopy.geocoders import Nominatim
from urllib import error
import time
import urllib.request
import json
import urllib
import os
import urllib.parse
import logging
#
# PM Weather API  
#
# /search/<location>
# Searches the Geonames database for the corresponding location, takes the coordinates of the first results and sends them to the Darksky API request. Fetches full data if no further endpoint is specified. (/current, /basic, /forecast, /<unix_timestamp> for detailed requests). e.g. /search/helsinki/current
#
#
# /estonian_map (/<one_of_15_cities>)
# Estonian map. Endpoint pulls the basic weather information for the 15 county capitals of Estonia. (All together or separately). Displays the name of the city, icon, temperature, apparent temperature, wind speed, wind direction and a verbal summary (in English).
#
#
# /<one_of_15_cities>
# Fetches the Darksky API full data for one of the cities. (/current, /basic, /forecast, /<unix_timestamp>  for detailed requests). e.g. /jõhvi/forecast
#
#
# /coordinates/<coordinates>
# Works the same way as ‘/search’. (/current; /forecast, /basic, /<unix_timestamp> for detailed requests) e.g. /coordinates/59.4372,24.7454
# Coordinates also gives the address of the specified coordinates. Its JSON field is 'address' e.g "19, Väike-Tähe, Kesklinn, Tartu, Tartu maakond, 50103, Eesti",
#
#
# endpoints:
# /current: displays the current information
# /forecast: displays the information for the following week
# /basic: displays basic information for today, tomorrow and the day after tomorrow
# /<unix_timestamp>: displays a full data request for the specified time. e.g. /1476738000
#
# Every response is in JSON: first element is 'location' and every 'location' has a 'name' attribute. (Coordinates has an 'address' field instead.)
#
#
# 15 cities (county capitals of Estonia):
# Tallinn
# Tartu
# Viljandi
# Pärnu
# Haapsalu
# Jõgeva
# Kärdla
# Kuressaare
# Võru
# Rakvere
# Paide
# Rapla
# Jõhvi
# Põlva
# Valga
#

API_KEY = os.environ['API_KEY']

GRAYLOG_SERVER_HOST = os.environ['GRAYLOG_SERVER_HOST']

GRAYLOG_SERVER_PORT = 12201
if 'GRAYLOG_SERVER_PORT' in os.environ:
    GRAYLOG_SERVER_PORT = os.environ['GRAYLOG_SERVER_PORT']

APP_PORT = 80
if 'APP_PORT' in os.environ:
    APP_PORT = os.environ['APP_PORT']

APP_URL_PREFIX = ''
if 'APP_URL_PREFIX' in os.environ:
    APP_URL_PREFIX = os.environ['APP_URL_PREFIX']

DARK_SKY_URL = 'https://api.darksky.net/forecast/'

DARK_SKY_SUFFIX = '?units=si&lang=et'
if 'DARK_SKY_SUFFIX' in os.environ:
    DARK_SKY_SUFFIX = os.environ['DARK_SKY_SUFFIX']

DARK_SKY_UNIX_SUFFIX = '?exclude=currently&lang=et&units=si'
bp = Blueprint('weather', __name__,
               template_folder='templates')

GEONAMES_URL = 'http://api.geonames.org/searchJSON?name='

geolocator = Nominatim()

CURRENT_TIME = int(time.time())
DAY_IN_SECONDS = 86400
WEEK_IN_DAYS = 7

# 15 county capitals of Estonia
capitalCities = {
    'tallinn': DARK_SKY_URL + API_KEY + '/59.4372,24.7454',
    'tartu': DARK_SKY_URL + API_KEY + '/58.3727,26.7238',
    'viljandi': DARK_SKY_URL + API_KEY + '/58.3563,25.5851',
    'pärnu': DARK_SKY_URL + API_KEY + '/58.3801,24.52',
    'haapsalu': DARK_SKY_URL + API_KEY + '/58.9339,23.5428',
    'jõgeva': DARK_SKY_URL + API_KEY + '/58.7441,26.3872',
    'kärdla': DARK_SKY_URL + API_KEY + '/58.9943,22.7459',
    'kuressaare': DARK_SKY_URL + API_KEY + '/58.2528,22.4849',
    'võru': DARK_SKY_URL + API_KEY + '/57.8356,27.0028',
    'rakvere': DARK_SKY_URL + API_KEY + '/59.3453,26.3619',
    'paide': DARK_SKY_URL + API_KEY + '/58.8869,25.5699',
    'rapla': DARK_SKY_URL + API_KEY + '/58.9992,24.8047',
    'jõhvi': DARK_SKY_URL + API_KEY + '/59.358,27.4189',
    'põlva': DARK_SKY_URL + API_KEY + '/58.0536,27.0583',
    'valga': DARK_SKY_URL + API_KEY + '/57.7799,26.0628'
}


def dumpjson(dict):
    return json.dumps(dict, ensure_ascii=False).encode('utf-8')


def encoding(slug):
    slug = urllib.parse.quote(slug.lower().encode('utf8'))
    return slug


def getGeoNames(slug):
    url = GEONAMES_URL + slug + '&featureClass=A&featureClass=P&maxRows=10&username=valgev6lur'
    return url


def iround(x):
    y = round(x) - .5
    return int(y) + (y > 0)


def getURL(location, unix=None):
    location = location.lower()
    if unix is not None:
        return DARK_SKY_URL + API_KEY + '/' + location + ',' + unix + DARK_SKY_UNIX_SUFFIX
    return DARK_SKY_URL + API_KEY + '/' + location + DARK_SKY_SUFFIX


def parseJson(url, Class):
    try:
        parsingJson = urllib.request.urlopen(url).read()
        html = str(parsingJson, 'utf-8')
        jsonReady = json.loads(html)
        result = Class(jsonReady)
        return result
    except error.HTTPError as e:
        abort(e.code)
    except ImportError:
        abort(500)


# Search for locations around the world. This method returns a DarkSky API request,
# JSON-formatted. It uses Geonames to get the coordinates for a certain location.
# If a location was not found, it will return an error.
@bp.route('/search/<location>')
def search_location(location):
    try:
        url = getGeoNames(encoding(location))
    except NameError:
        abort(404)
    try:
        geoName = parseJson(url, Geonames)
        coordinates = geoName.getCoordinates(0)
        forDarkSky = getURL(coordinates)
        darkSky = parseJson(forDarkSky, DarkSky)
        fulldict = {}
        fulldict['location'] = darkSky.data
        fulldict['location']['name'] = location.title()
        fulldict['location']['coordinates'] = coordinates
        output = dumpjson(fulldict)
    except IndexError:
        output = abort(404)
    return output


# Returns the current (or forecast) dataset for the searched location. Used to
# fill the current (or future) weather information box
@bp.route('/search/<location>/<endpoint>')
def search_location_endpoints(location, endpoint):
    try:
        url = getGeoNames(encoding(location))
    except NameError:
        abort(404)
    try:
        geoName = parseJson(url, Geonames)
        coordinates = geoName.getCoordinates(0)
        forDarkSky = getURL(coordinates)
        darkSky = parseJson(forDarkSky, DarkSky)
        fulldict = {}
        if endpoint == 'current':
            darkSky.data['currently']['name'] = location.title()
            fulldict['location'] = darkSky.data['currently']
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        elif endpoint == 'forecast':
            darkSky.data['daily']['name'] = location.title()
            fulldict['location'] = darkSky.data['daily']
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        elif endpoint == 'basic':
            fulldict['location'] = darkSky.basicforecast()
            fulldict['location']['name'] = location.title()
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        else:
            url = getURL(coordinates, endpoint)
            locationUNIX = parseJson(url, DarkSky)
            fulldict[location.getName(0)] = locationUNIX.data
            output = dumpjson(fulldict)
    except IndexError:
        output = abort(404)
    return output


# Returns the full dataset for the specified coordinates (address based on the location is included)
@bp.route('/coordinates/<coordinates>')
def coordinates(coordinates):
    try:
        url = getURL(coordinates)
    except NameError:
        abort(404)
    try:
        fulldict = {}
        location = parseJson(url, DarkSky)
        name = geolocator.reverse(coordinates)
        fulldict['location'] = location.data
        fulldict['location']['address'] = name.address
        fulldict['location']['coordinates'] = coordinates
        output = dumpjson(fulldict)
    except NameError:
        output = abort(404)
    return output


# Detailed response with coordinates
@bp.route('/coordinates/<coordinates>/<endpoint>')
def coordinates_endpoints(coordinates, endpoint):
    try:
        url = getURL(coordinates)
    except NameError:
        abort(404)
    try:
        fulldict = {}
        darkSky = parseJson(url, DarkSky)
        name = geolocator.reverse(coordinates)
        if endpoint == 'current':
            darkSky.data['currently']['address'] = name.address
            fulldict['location'] = darkSky.data['currently']
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        elif endpoint == 'forecast':
            darkSky.data['daily']['address'] = name.address
            fulldict['location'] = darkSky.data['daily']
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        elif endpoint == 'basic':
            fulldict['location'] = darkSky.basicforecast()
            fulldict['location']['address'] = name.address
            fulldict['location']['coordinates'] = coordinates
            output = dumpjson(fulldict)
        else:
            url = getURL(coordinates, endpoint)
            locationUNIX = parseJson(url, DarkSky)
            fulldict[name.address] = locationUNIX.data
            output = dumpjson(fulldict)
    except NameError:
        output = abort(404)
    return output


# Returns the whole JSON data from the DarkSky API request. This method
# uses one of the predetermined cities (15 county capitals) or a location
# based on coordinates.
@bp.route('/<city_name>')
def cities(city_name):
    try:
        url = capitalCities[city_name] + DARK_SKY_SUFFIX
    except KeyError:
        abort(404)
    try:
        fulldict = {}
        location = parseJson(url, DarkSky)
        fulldict['location'] = location.data
        fulldict['location']['name'] = city_name.title()
        output = dumpjson(fulldict)
    except NameError:
        output = abort(404)
    return output


# One of 15 cities in Estonia and the requested information for that. The 15 biggest locations
# in Estonia are good for caching.
@bp.route('/<city_name>/<endpoint>')
def cities_endpoints(city_name, endpoint):
    try:
        url = capitalCities[city_name] + DARK_SKY_SUFFIX
    except KeyError:
        abort(404)
    try:
        fulldict = {}
        darkSky = parseJson(url, DarkSky)
        if endpoint == 'current':
            darkSky.data['currently']['name'] = city_name.title()
            fulldict['location'] = darkSky.data['currently']
            output = dumpjson(fulldict)
        elif endpoint == 'forecast':
            darkSky.data['daily']['name'] = city_name.title()
            fulldict['location'] = darkSky.data['daily']
            output = dumpjson(fulldict)
        elif endpoint == 'basic':
            fulldict['location'] = darkSky.basicforecast()
            fulldict['location']['name'] = city_name.title()
            output = dumpjson(fulldict)
        else:
            if city_name in capitalCities:
                url = capitalCities[city_name] + ',' + endpoint + DARK_SKY_UNIX_SUFFIX
            else:
                url = getURL(city_name, endpoint)
            locationUNIX = parseJson(url, DarkSky)
            output = json.dumps(locationUNIX.data, ensure_ascii=False).encode('utf-8')
    except NameError:
        output = abort(404)
    return output


# Returns the current 7 attributes for the 15 county capitals of Estonia. Used to populate the map
@bp.route('/estonian_map')
def get_estonian_map():
    eesti_kaart = {}
    for i in capitalCities.keys():
        eesti_kaart[i] = json.loads(get_city_for_map(i).decode('utf-8'))
    return dumpjson(eesti_kaart)


# Returns one of 15 cities in Estonia. These 15 predetermined cities
# are used to fill the Estonian map with data. This method returns the
# name of the city, icon for the current weather and current temperature
@bp.route('/estonian_map/<city_name>')
def get_city_for_map(city_name):
    try:
        url = capitalCities[city_name] + DARK_SKY_SUFFIX
    except KeyError:
        abort(404)
    try:
        location = parseJson(url, DarkSky)
        output = json.dumps({'name': city_name.title(), 'icon': location.icon,
                             'temperature': iround(location.temperature),
                             'apparentTemperature': iround(location.apparentTemperature),
                             'windSpeed': iround(location.windSpeed),
                             'windBearing': location.windBearing,
                             'summary': location.summary},
                            ensure_ascii=False).encode('utf-8')
    except NameError:
        output = abort(404)
    return output


@bp.route('/test/<error_code>')
def error500(error_code):
    abort(int(error_code))


@bp.errorhandler(404)
def fourofour(e):
    return make_response(jsonify({'error': 'Error 404 Not Found'}), 404)


@bp.errorhandler(500)
def fiveoo(e):
    return make_response(jsonify({'error': 'Error 500 Internal Server Error'}), 500)


@bp.errorhandler(503)
def fiveothree(e):
    return make_response(jsonify({'error': 'Error 503 Service Unavailable'}), 503)


@bp.after_request
def add_header(response):
    response.cache_control.max_age = 300
    response.content_type = 'application/json; charset=utf-8'
    return response


app = Flask(__name__)
app.register_blueprint(bp, url_prefix=APP_URL_PREFIX)
CORS(app, resources=r'/*')

app.config['GRAYLOG_HOST'] = GRAYLOG_SERVER_HOST
app.config['GRAYLOG_PORT'] = int(GRAYLOG_SERVER_PORT)
graylog = Graylog(app)

graylog.info('Message', extra={
    'extra': 'metadata',
})

logger = logging.getLogger(__name__)
logger.addHandler(graylog.handler)
logger.info('Message')

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=int(APP_PORT))
