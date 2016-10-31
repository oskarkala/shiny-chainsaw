def iround(x):
    y = round(x) - .5
    return int(y) + (y > 0)


class DarkSky:
    def __init__(self, location):
        self.data = location
        try:
            self.apparentTemperature = self.data['currently']['apparentTemperature']
        except KeyError:
            self.apparentTemperature = None
        try:
            self.cloudCover = self.data['currently']['cloudCover']
        except KeyError:
            self.cloudCover = None
        try:
            self.dewPoint = self.data['currently']['dewPoint']
        except KeyError:
            self.dewPoint = None
        try:
            self.humidity = self.data['currently']['humidity']
        except KeyError:
            self.humidity = None
        try:
            self.icon = self.data['currently']['icon']
        except KeyError:
            self.icon = None
        try:
            self.ozone = self.data['currently']['ozone']
        except KeyError:
            self.ozone = None
        try:
            self.precipIntensity = self.data['currently']['precipIntensity']
        except KeyError:
            self.precipIntensity = None
        try:
            self.precipProbability = self.data['currently']['precipProbability']
        except KeyError:
            self.precipProbability = None
        try:
            self.precipType = self.data['currently']['precipType']
        except KeyError:
            self.precipType = None
        try:
            self.pressure = self.data['currently']['pressure']
        except KeyError:
            self.pressure = None
        try:
            self.summary = self.data['currently']['summary']
        except KeyError:
            self.summary = None
        try:
            self.temperature = self.data['currently']['temperature']
        except KeyError:
            self.temperature = None
        try:
            self.time = self.data['currently']['time']
        except KeyError:
            self.time = None
        try:
            self.visibility = self.data['currently']['visibility']
        except KeyError:
            self.visibility = None
        try:
            self.windBearing = self.data['currently']['windBearing']
        except KeyError:
            self.windBearing = None
        try:
            self.windSpeed = self.data['currently']['windSpeed']
        except KeyError:
            self.windSpeed = None

    def basicforecast(self):
        forecast = {}
        forecast['today'] = {'temperature': iround(self.temperature),
                             'apparentTemperature': iround(self.apparentTemperature),
                             'icon': self.icon,
                             'summary': self.summary}

        forecast['tomorrow'] = {'medianTemperature': iround((self.data['daily']['data'][1]['temperatureMax']
                                                       + self.data['daily']['data'][1]['temperatureMin']) / 2),
                                'temperatureMin': iround(self.data['daily']['data'][1]['temperatureMin']),
                                'temperatureMax': iround(self.data['daily']['data'][1]['temperatureMax']),
                                'medianApparentTemperature': iround((self.data['daily']['data'][1]['apparentTemperatureMax']
                                                       + self.data['daily']['data'][1]['apparentTemperatureMin']) / 2),
                                'icon': self.data['daily']['data'][1]['icon'],
                                'summary': self.data['daily']['data'][1]['summary']}

        forecast['dayAfterTomorrow'] = {'medianTemperature': iround((self.data['daily']['data'][2]['temperatureMax']
                                                       + self.data['daily']['data'][2]['temperatureMin']) / 2),
                                        'temperatureMin': iround(self.data['daily']['data'][2]['temperatureMin']),
                                        'temperatureMax': iround(self.data['daily']['data'][2]['temperatureMax']),
                                        'medianApparentTemperature': iround((self.data['daily']['data'][2]['apparentTemperatureMax']
                                                       + self.data['daily']['data'][2]['apparentTemperatureMin']) / 2),
                                        'icon': self.data['daily']['data'][2]['icon'],
                                        'summary': self.data['daily']['data'][2]['summary']}

        return forecast
