
class Location:
    def __init__(self, latitude, longitude):
        self.longitude = longitude
        self.latitude = latitude
    def __unicode__(self):
        return "%f,%f" % (self.latitude, self.longitude)
