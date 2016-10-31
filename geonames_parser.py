class Geonames:
    def __init__(self, location):
        self.data = location

    def getCoordinates(self, i):
        return self.data['geonames'][i]['lat'] + ',' + self.data['geonames'][i]['lng']

    def getName(self, i):
        return self.data['geonames'][i]['name']