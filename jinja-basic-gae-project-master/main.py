#!/usr/bin/env python
import os
import jinja2
import webapp2
from models import Sporocilo
from google.appengine.api import users
import json
from google.appengine.api import urlfetch
api_key="2b9448f3b7960c3e992c3d62064c5f19"

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        user = users.get_current_user()
        if user:
            params["logged_in"] = True
            params["email"] = user.email()
            params["email"]=user.email()
            params["logout_url"] = users.create_logout_url('/')
        else:
            params["logged_in"] = False
            params["login_url"] = users.create_login_url('/')
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user=users.get_current_user()
        if user:
            return self.redirect_to("rezultat")
        return self.render_template("main.html")

class BmailHandler(BaseHandler):
    def get(self):
        sporocilo=Sporocilo.query(Sporocilo.izbrisano == False).fetch()
        params={"sporocilo":sporocilo}
        return self.render_template("hello.html", params=params)
    def post(self):
        user=users.get_current_user()
        email=user.email()
        naslovnik=self.request.get("naslovnik")
        sporocilo=self.request.get("sporocilo")
        sporocilo_object=Sporocilo(naslovnik=naslovnik, email=email, vnos=sporocilo)
        sporocilo_object.put()

        return self.redirect_to("seznam-sporocil")




class SeznamSporocilHandler(BaseHandler):
    def get(self):
        seznam=Sporocilo.query(Sporocilo.izbrisano == False).fetch()
        params={"seznam":seznam}
        return self.render_template("seznam-sporocil.html", params=params)

class PosameznoSporociloHandler(BaseHandler):
    def get(self, id):
        sporocilo = Sporocilo.get_by_id(int(id))
        params={"sporocilo":sporocilo}
        return self.render_template("posamezno_sporocilo.html", params=params)

class PrejetaSporocilaHandler(BaseHandler):
    def get(self):
        user=users.get_current_user()
        email=user.email()
        seznam=Sporocilo.query(Sporocilo.izbrisano == False and email == Sporocilo.naslovnik).fetch()
        params={"seznam": seznam}
        return self.render_template("prejeta_sporocila.html", params=params)


class UrediSporociloHandler(BaseHandler):
    def get(self, id):
        sporocilo=Sporocilo.get_by_id(int(id))
        params={"sporocilo":sporocilo}
        return self.render_template("uredi_sporocilo.html", params=params)
    def post(self, id):
        vnos=self.request.get("vnos")
        sporocilo=Sporocilo.get_by_id(int(id))
        sporocilo.vnos=vnos
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")

class IzbrisiSporociloHandler(BaseHandler):
    def get(self, id):
        sporocilo=Sporocilo.get_by_id(int(id))
        params={"sporocilo": sporocilo}
        return self.render_template("izbrisi_sporocilo.html", params=params)
    def post(self, id):
        sporocilo=Sporocilo.get_by_id(int(id))
        sporocilo.izbrisano=True
        sporocilo.put()
        return self.redirect_to("seznam-sporocil")

class WeatherHandler(BaseHandler):
    def get(self):
        return self.render_template("weather.html")
    def post(self):
        location = self.request.get("location")
        url ="http://api.openweathermap.org/data/2.5/weather?q=%s&units=metric&appid=%s" % (location, api_key)
        result = urlfetch.fetch(url)
        json_data=json.loads(result.content)
        params = {"data": json_data}

        return self.render_template("weather.html", params=params)

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/rezultat', BmailHandler, name="rezultat"),
    webapp2.Route('/prejeta-sporocila', PrejetaSporocilaHandler),
    webapp2.Route('/seznam-sporocil', SeznamSporocilHandler, name="seznam-sporocil"),
    webapp2.Route('/sporocilo/<id:\d+>', PosameznoSporociloHandler),
    webapp2.Route('/sporocilo/<id:\d+>/uredi',UrediSporociloHandler),
    webapp2.Route('/sporocilo/<id:\d+>/izbrisi',IzbrisiSporociloHandler),
    webapp2.Route('/vreme', WeatherHandler),

], debug=True)
