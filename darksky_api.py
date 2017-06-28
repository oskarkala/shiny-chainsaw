# -*- coding: utf-8 -*-
from flask import Flask, abort, Blueprint, jsonify, make_response
from flask_cors import CORS
from flask_graylog_local import Graylog
from location_class import DarkSky
from geonames_parser import Geonames
from geopy.geocoders import Nominatim
from urllib import error
from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
import multiprocessing
import time
import urllib.request
import json
import urllib
import os
import urllib.parse


#
# PM Weather API  
#
# /<language>/<location>
# Searches the Geonames database for the corresponding location, takes the coordinates of the first results and sends them to the Darksky API request. Fetches full data if no further endpoint is specified. (/current, /basic, /forecast for detailed requests). e.g. et/helsinki/current
#
# /coordinates/<coordinates>
# Works the same way as ‘/search’. (/current; /forecast, /basic for detailed requests) e.g. ru/coordinates/59.4372,24.7454
# Coordinates also gives the address of the specified coordinates. Its JSON field is 'address' e.g "19, Väike-Tähe, Kesklinn, Tartu, Tartu maakond, 50103, Eesti",
#
# endpoints:
# /current: displays the current information
# /forecast: displays the information for the following week
# /basic: displays basic information for today, tomorrow and the day after tomorrow
#
# languages:
# et for Estonian
# ru for Russian
# en for English
# lv for Latvian
#
# Every response is in JSON: first element is 'location' and every 'location' has a 'name' attribute. (Coordinates has an 'address' field instead.)
#


API_KEY = os.environ['API_KEY']

GRAYLOG_SERVER_HOST = os.environ['GRAYLOG_SERVER_HOST']
#GRAYLOG_SERVER_HOST = 'graylog.emeedia.eu'

GRAYLOG_SERVER_PORT = 12201
if 'GRAYLOG_SERVER_PORT' in os.environ:
    GRAYLOG_SERVER_PORT = os.environ['GRAYLOG_SERVER_PORT']

APP_PORT = 80
if 'APP_PORT' in os.environ:
    APP_PORT = os.environ['APP_PORT']

APP_URL_PREFIX = ''
if 'APP_URL_PREFIX' in os.environ:
    APP_URL_PREFIX = os.environ['APP_URL_PREFIX']

CPU_COUNT = multiprocessing.cpu_count()
DARK_SKY_URL = 'https://api.darksky.net/forecast/'

bp = Blueprint('weather', __name__,
               template_folder='templates')

GEONAMES_URL = 'http://api.geonames.org/searchJSON?q='

geolocator = Nominatim()


def getDarkSkySUFFIX(lang):
    if lang == 'et':
        return '?units=si&lang=et'
    elif lang == 'en':
        return '?units=si'
    elif lang == 'ru':
        return '?units=si&lang=ru'
    elif lang == 'lv':
        return '?units=si&lang=lv'
    else:
        return abort(400)


def checkLang(lang):
    if lang == 'et' or lang == 'ru' or lang == 'en' or lang == 'lv':
        return make_response(jsonify({'error': 'Specify a location'}))
    else:
        return abort(400)


def dumpjson(dict):
    return json.dumps(dict, ensure_ascii=False).encode('utf-8')


def encoding(slug):
    slug = urllib.parse.quote(slug.lower().encode('utf8'))
    return slug


def getGeoNames(location):
    url = GEONAMES_URL + location + '&featureClass=A&featureClass=P&maxRows=10&username=valgev6lur'
    return url


def iround(x):
    y = round(x) - .5
    return int(y) + (y > 0)


def getURL(location, lang):
    location = location.lower()
    return DARK_SKY_URL + API_KEY + '/' + location + getDarkSkySUFFIX(lang)


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


def graylogger(e):
   graylog.error(e, extra={
       'extra': 'metadata',
   })


@bp.route('/<lang>')
def nothing(lang):
    return checkLang(lang)


# Search for locations around the world. This method returns a DarkSky API request,
# JSON-formatted. It uses Geonames to get the coordinates for a certain location.
# If a location was not found, it will return an error.
@bp.route('/<lang>/<location>')
def search_location(location, lang):
    try:
        url = getGeoNames(encoding(location))
    except NameError:
        abort(404)
    try:
        geoName = parseJson(url, Geonames)
        coordinates = geoName.getCoordinates(0)
        forDarkSky = getURL(coordinates, lang)
        darkSky = parseJson(forDarkSky, DarkSky)
        fulldict = {}
        fulldict['location'] = darkSky.data
        fulldict['location']['name'] = location.title()
        output = dumpjson(fulldict)
    except IndexError:
        output = abort(404)
    return output


# Returns the current (or forecast) dataset for the searched location. Used to
# fill the current (or future) weather information box
@bp.route('/<lang>/<location>/<endpoint>')
def search_location_endpoints(location, lang, endpoint):
    try:
        url = getGeoNames(encoding(location))
    except NameError:
        abort(404)
    try:
        geoName = parseJson(url, Geonames)
        coordinates = geoName.getCoordinates(0)
        forDarkSky = getURL(coordinates, lang)
        darkSky = parseJson(forDarkSky, DarkSky)
        fulldict = {}
        if endpoint == 'current':
            darkSky.data['currently']['name'] = location.title()
            fulldict['location'] = darkSky.data['currently']
            fulldict['location']['latitude'] = darkSky.data['latitude']
            fulldict['location']['longitude'] = darkSky.data['longitude']
            output = dumpjson(fulldict)
        elif endpoint == 'forecast':
            darkSky.data['daily']['name'] = location.title()
            fulldict['location'] = darkSky.data['daily']
            output = dumpjson(fulldict)
        elif endpoint == 'basic':
            fulldict['location'] = darkSky.basicforecast()
            fulldict['location']['name'] = location.title()
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
@bp.route('/<lang>/coordinates/<coordinates>')
def coordinates(coordinates, lang):
    try:
        url = getURL(coordinates, lang)
    except NameError:
        abort(404)
    try:
        fulldict = {}
        location = parseJson(url, DarkSky)
        name = geolocator.reverse(coordinates)
        fulldict['location'] = location.data
        fulldict['location']['address'] = name.address
        output = dumpjson(fulldict)
    except NameError:
        output = abort(404)
    return output


# Detailed response with coordinates
@bp.route('/<lang>/coordinates/<coordinates>/<endpoint>')
def coordinates_endpoints(lang, coordinates, endpoint):
    try:
        url = getURL(coordinates, lang)
    except NameError:
        abort(404)
    try:
        fulldict = {}
        darkSky = parseJson(url, DarkSky)
        name = geolocator.reverse(coordinates)
        if endpoint == 'current':
            darkSky.data['currently']['address'] = name.address
            fulldict['location'] = darkSky.data['currently']
            output = dumpjson(fulldict)
        elif endpoint == 'forecast':
            darkSky.data['daily']['address'] = name.address
            fulldict['location'] = darkSky.data['daily']
            output = dumpjson(fulldict)
        elif endpoint == 'basic':
            fulldict['location'] = darkSky.basicforecast()
            fulldict['location']['address'] = name.address
            output = dumpjson(fulldict)
        else:
            url = getURL(coordinates, endpoint)
            locationUNIX = parseJson(url, DarkSky)
            fulldict[name.address] = locationUNIX.data
            output = dumpjson(fulldict)
    except NameError:
        output = abort(404)
    return output


estonian_map = {
    'Tallinn,Estonia',
    'Tartu,Estonia',
    'Pärnu,Estonia',
    'Antsla,Estonia',
    'Elva,Estonia',
    'Haapsalu,Estonia',
    'Jõgeva,Estonia',
    'Jõhvi,Estonia',
    'Kallaste,Estonia',
    'Karksi-Nuia,Estonia',
    'Kehra,Estonia',
    'Keila,Estonia',
    'Kihnu,Estonia',
    'Kilingi-Nõmme,Estonia',
    'Kiviõli,Estonia',
    'Kohtla-Järve,Estonia',
    'Kunda,Estonia',
    'Kuressaare,Estonia',
    'Kärdla,Estonia',
    'Loksa,Estonia',
    'Maardu,Estonia',
    'Mõisaküla,Estonia',
    'Mustvee,Estonia',
    'Narva,Estonia',
    'Narva-Jõesuu,Estonia',
    'Otepää,Estonia',
    'Paide,Estonia',
    'Paldiski,Estonia',
    'Põltsamaa,Estonia',
    'Põlva,Estonia',
    'Rakvere,Estonia',
    'Rapla,Estonia',
    'Räpina,Estonia',
    'Ruhnu,Estonia',
    'Saue,Estonia',
    'Sillamäe,Estonia',
    'Tapa,Estonia',
    'Tõrva,Estonia',
    'Türi,Estonia',
    'Valga,Estonia',
    'Viljandi,Estonia',
    'Võhma,Estonia',
    'Võru,Estonia'}

european_map = {
    'Albania,Tirana',
    'Andorra la Vella',
    'Austria,Vienna',
    'Belarus,Minsk',
    'Belgium,Brussels',
    'Sarajevo',
    'Bulgaria,Sofia',
    'Croatia,Zagreb',
    'Cyprus,Nicosia',
    'Czechia,Prague',
    'Denmark,Copenhagen',
    'Estonia,Tallinn',
    'Finland,Helsinki',
    'France,Paris',
    'Georgia,Tbilisi',
    'Germany,Berlin',
    'Greece,Athens',
    'Hungary,Budapest',
    'Iceland,Reykjavik',
    'Ireland,Dublin',
    'Italy,Rome',
    'Latvia,Riga',
    'Liechtenstein,Vaduz',
    'Lithuania,Vilnius',
    'Luxembourg',
    'Macedonia,Skopje',
    'Malta,Valletta',
    'Moldova,Chisinau',
    'Monaco,Monaco',
    'Montenegro,Podgorica',
    'Netherlands,Amsterdam',
    'Norway,Oslo',
    'Poland,Warsaw',
    'Portugal,Lisbon',
    'Romania,Bucharest',
    'Russia,Moscow',
    'San Marino',
    'Serbia,Belgrade',
    'Slovakia,Bratislava',
    'Slovenia,Ljubljana',
    'Spain,Madrid',
    'Sweden,Stockholm',
    'Switzerland,Bern',
    'Turkey,Ankara',
    'Ukraine,Kiev',
    'United Kingdom,London',
    'Vatican'
}


def create_map(location, lang):
    try:
        url = getGeoNames(encoding(location))
    except NameError:
        abort(404)
    try:
        geoName = parseJson(url, Geonames)
        coordinates = geoName.getCoordinates(0)
        forDarkSky = getURL(coordinates, lang)
        darkSky = parseJson(forDarkSky, DarkSky)
        fulldict = {}
        fulldict['location'] = darkSky.data
        fulldict['location']['name'] = location.title()
        output = dumpjson(fulldict)
    except IndexError:
        output = abort(404)
    return output


@bp.route('/<lang>/map/<area>')
def map(lang, area):

    start = time.time()
    try:
        if area == 'europe':
           map = european_map
        elif area == 'estonia':
           map = estonian_map

        pool = ThreadPool(len(map))
        json_array = {}
        pooled_list = pool.map(partial(search_location, lang=lang), map)

        for item in pooled_list:
            item = json.loads(str(item, 'utf-8'))
            json_array[item['location']['name']] = item
        output = dumpjson(json_array)

        pool.close()
        pool.join()

    except NameError:
        output = abort(404)

    end = time.time()
    print("Time elapsed with the request: ", end-start)
    return output


@bp.route('/error/<slug>')
def error_slug(slug):
    if slug == '400':
        output = abort(400)
    elif slug == '404':
        output = abort(404)
    elif slug == '500':
        output = abort(500)
    elif slug == '503':
        output = abort(503)
    elif slug == '504':
        output = abort(504)
    else:
        output = 'output'
    return output


@bp.app_errorhandler(400)
def fouroo(e):
    graylogger(e)
    return make_response(jsonify({'error': 'Error 400 Bad Request'}), 400)


@bp.errorhandler(404)
def fourofour(e):
    graylogger(e)
    return make_response(jsonify({'error': 'Error 404 Not Found'}), 404)


@bp.app_errorhandler(500)
def fiveoo(e):
    graylogger(e)
    return make_response(jsonify({'error': 'Error 500 Internal Server Error'}), 500)


@bp.errorhandler(503)
def fiveothree(e):
    graylogger(e)
    return make_response(jsonify({'error': 'Error 503 Service Unavailable'}), 503)


@bp.errorhandler(504)
def fiveofour(e):
    graylogger(e)
    return make_response(jsonify({'error': 'Error 504 Gateway Timeout'}), 503)


@bp.after_request
def add_header(response):
    response.cache_control.max_age = 900
    response.content_type = 'application/json; charset=utf-8'
    return response


app = Flask(__name__)
app.register_blueprint(bp, url_prefix=APP_URL_PREFIX)
CORS(app, resources=r'/*')

app.config['GRAYLOG_HOST'] = GRAYLOG_SERVER_HOST
app.config['GRAYLOG_PORT'] = int(GRAYLOG_SERVER_PORT)
graylog = Graylog(app)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=int(APP_PORT))
    app.run()
