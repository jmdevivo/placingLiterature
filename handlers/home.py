""" home page request handlers """
# pylint
import json
import logging
import random

from google.appengine.ext import webapp

from classes import placedlit

from handlers.abstracts import baseapp

import blogposts


class HomeHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'Home'
    posts = blogposts.BlogpostsHandler.posts_for_display()
    bloglinks = [{'title': post.title, 'link': post.link} for post in posts]
    template_values['posts'] = bloglinks
    template_values['remote_addr'] = self.request.remote_addr
    self.render_template('home.tmpl', template_values)


class AboutHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'About'
    self.render_template('about.tmpl', template_values)


class FundingHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'Funding'
    self.render_template('funding.tmpl', template_values)


class MapHandler(baseapp.BaseAppHandler):
  def get(self, location=None, key=None):
    template_values = self.basic_template_content()
    template_values['title'] = 'Map'
    if location and ',' in location:
      (lat, lng) = location.replace('/', '').split(',')
      template_values['center'] = '{lat:%s,lng:%s}' % (lat, lng)
    if self.request.get('key'):
      template_values['key'] = self.request.get('key')
    self.render_template('map.tmpl', template_values)


class IndexedSceneMapHandler(baseapp.BaseAppHandler):
  def get(self, location=None, key=None):
    template_values = self.basic_template_content()
    template_values['title'] = 'Map'
    key = self.request.get('key')
    lat = self.request.get('lat')
    # FIXIT- Pick one: 'lon', 'lng'
    if self.request.get('lon'):
      lng = self.request.get('lon')
    else:
      lng = self.request.get('lng')
    if lat and lng:  # lat, lng with no scene
      logging.info('got lat, lng in query string')
      template_values['center'] = '{lat:%s,lng:%s}' % (lat, lng)
      template_values['scenes'] = self.get_nearby_places_json(lat=lat, lng=lng)
    elif key:  # scene but no lat, lng
      logging.info('got key')
      template_values['key'] = key
      scene_doc = placedlit.get_search_doc_for_scene(key)
      if scene_doc:
        scene = self.format_location_index_doc(scene_doc)
        lat = scene['latitude']
        lng = scene['longitude']
        template_values['center'] = '{lat:%s,lng:%s}' % (lat, lng)
        template_values['scenes'] = self.get_nearby_places_json(lat=lat,
                                                                lng=lng)
      else:
        logging.debug('no doc in location index for %s', key)
    elif location and ',' in location:
      logging.info('got location in path')
      (lat, lng) = location.replace('/', '').split(',')
      template_values['center'] = '{lat:%s,lng:%s}' % (lat, lng)
      template_values['key'] = key
    self.render_template('map.tmpl', template_values)

  def get_nearby_places_json(self, lat=None, lng=None):
    places = placedlit.get_nearby_places(lat, lng, sorted=True)
    if places:
      return json.dumps(self.format_location_index_results(places))
    else:
     return None


class UserstatusHandler(baseapp.BaseAppHandler):
  def get(self):
    return self.get_user_status()


class AllscenesHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'All Scenes'
    self.render_template('all.tmpl', template_values)


class AdminEditSceneHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'Edit Scene'
    place_id = self.request.get('key')
    place = placedlit.PlacedLit.get_place_from_id(place_id)
    template_values['place'] = place
    self.render_template('edit.tmpl', template_values)

  def post(self):
    """ add scene from user submission """
    place = placedlit.PlacedLit.get_place_from_id(self.request.get('key'))
    if place:
      place_data = dict()
      update_fields = ['title', 'author', 'scenelocation', 'scenedescription',
                       'notes', 'image_url', 'actors', 'scenetime', 'symbols',
                       'ug_isbn']
      for field in update_fields:
        place_data[field] = self.request.get(field)
      place.update_fields(place_data)
      self.response.out.write('Saved')

  def delete(self):
    logging.info('deleted %s', self.request.get('key'))
    place = placedlit.PlacedLit.get_place_from_id(self.request.get('key'))
    place.delete_scene()
    self.response.out.write('Deleted')


class NewhomeHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'Home'
    posts = blogposts.BlogpostsHandler.posts_for_display()
    bloglinks = [{'title': post.title, 'link': post.link} for post in posts]
    template_values['posts'] = bloglinks
    self.render_template('placinglit.tmpl', template_values)


class MapFilterHandler(baseapp.BaseAppHandler):
  def get(self, field=None, term=None):
    template_values = self.basic_template_content()
    template_values['title'] = 'Map'
    places = placedlit.PlacedLit.places_by_query(field, term)
    loc_json = []
    if places:
      if field == 'author':
        loc_json = self.format_location_index_results(places)
      else:
        loc_json = [self.export_place_fields(place) for place in places]
    if loc_json:
      some_scene = random.choice(loc_json)
      template_values['center'] = '{{lat:{}, lng:{}}}'.format(
        some_scene['latitude'], some_scene['longitude'])
    template_values['scenes'] = json.dumps(loc_json)
    self.render_template('map.tmpl', template_values)


class AdminMenuHandler(baseapp.BaseAppHandler):
  def get(self):
    template_values = self.basic_template_content()
    template_values['title'] = 'Admin Menu'
    self.render_template('admin.tmpl', template_values)


urls = [
  ('/about', AboutHandler),
  ('/all', AllscenesHandler),
  ('/funding', FundingHandler),
  ('/home', HomeHandler),
  ('/map/filter/(.*)/(.*)', MapFilterHandler),
  ('/map(/?.*)', MapHandler),
  ('/', HomeHandler),
  ('/user/status', UserstatusHandler),
  ('/desktop/', NewhomeHandler),
  ('/admin/edit', AdminEditSceneHandler),
  ('/admin/menu', AdminMenuHandler),
]

app = webapp.WSGIApplication(urls, debug=True)
