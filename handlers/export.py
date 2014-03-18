"""
handlers.export
"""
# pylint: disable=C0103

import ast
import json
import logging

from google.appengine.ext import webapp
from google.appengine.api import users

from handlers.abstracts import baseapp
from classes import placedlit
# from classes import collections


class GetAllPlacesHandler(baseapp.BaseAppHandler):
  """ get all places as a json dump. useful for setting up dev environments """
  def get(self):
    places = placedlit.PlacedLit.get_all_places()
    loc_json = []
    for place in places:
      geo_pt = place.location
      location_export = {
        'latitude': geo_pt.lat,
        'longitude': geo_pt.lon
      }
      key = place.key()
      loc = {
        'title': place.title,
        'author': place.author,
        'scenelocation': place.scenelocation,
        'scenetime': place.scenetime,
        'actors': place.actors,
        'symbols': place.symbols,
        'scenedescription': place.scenedescription,
        'notes': place.notes,
        # 'ts': place.ts,
        'location': location_export,
        'checkins': place.checkins,
        'image_url': place.image_url,
        'db_key': key.id()}
      loc_json.append(loc)
    self.output_json(loc_json)


class QLDImportPlacesHandler(baseapp.BaseAppHandler):
  """ import qld places from csv """
  def post(self):
    data = json.loads(self.request.body)
    data['user'] = users.User('test@example.com')
    data['email'] = 'qld@qld.gov'
    if 'notes' not in data:
      data['notes'] = ''
    place_key = placedlit.PlacedLit.create_from_dict(data)
    print data['title'], place_key
    print place_key
    # collections.add_scene(place_key)


class ImportPlacesHandler(baseapp.BaseAppHandler):
  def post(self):
    data = {'actors': self.request.get('actors'),
            'author': self.request.get('author'),
            'current_checkin_count': int(self.request.get('checkins')),
            'notes': self.request.get('notes'),
            'scene': self.request.get('scenedescription'),
            'place_name': self.request.get('scenelocation'),
            'title': self.request.get('title'),
            'email': 'test@example.com'
            }
    data['user'] = users.User(data['email'])
    location = ast.literal_eval(self.request.get('location'))
    data['longitude'] = location['longitude']
    data['latitude'] = location['latitude']
    placedlit.PlacedLit.create_from_dict(data)


class MissingBookSceneHandler(baseapp.BaseAppHandler):
  def get(self):
    places = placedlit.PlacedLit.get_all_unresolved_places()
    place_json = []
    for place in places:
      geo_pt = place.location
      location_export = {
        'latitude': geo_pt.lat,
        'longitude': geo_pt.lon
      }
      key = place.key()
      loc = {
        'title': place.title,
        'author': place.author,
        'location': location_export,
        'checkins': place.checkins,
        'db_key': key.id()}

      if place.ug_isbn:
        loc['ug_isbn'] = place.ug_isbn
      else:
        loc['ug_isbn'] = ''

      place_json.append(loc)
    self.output_json(place_json)


urls = [
  ('/places/dump', GetAllPlacesHandler),
  ('/places/import', ImportPlacesHandler),
  ('/places/qld_import', QLDImportPlacesHandler),
  ('/places/missing_books', MissingBookSceneHandler)
]


app = webapp.WSGIApplication(urls, debug="True")
