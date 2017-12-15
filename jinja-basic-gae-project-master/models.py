from google.appengine.ext import ndb

class Sporocilo(ndb.Model):
    vnos=ndb.TextProperty()
    naslovnik=ndb.StringProperty()
    email=ndb.StringProperty()
    izbrisano=ndb.BooleanProperty(default=False)
    nastanek=ndb.DateTimeProperty(auto_now_add=True)
