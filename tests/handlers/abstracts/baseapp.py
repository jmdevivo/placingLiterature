"""
handlers.abstract.baseapp description.


Created on Nov 19, 2012
"""

__author__ = 'steven@eyeballschool.com (Steven)'

import json
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

TEMPLATE_DIRS = os.path.join(os.path.dirname(os.environ['PATH_TRANSLATED']),
                             '../templates')

FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576  # 1 MB
GM3_SSL_API_URL = 'https://maps-api-ssl.google.com/maps/api/js?v=3&sensor=true'
GM3_API_URL = 'http://maps.google.com/maps/api/js?sensor=true'
JSON_XSSI_PREFIX = None
GM3_API_KEY = 'AIzaSyBILv0WzDmEWQ3CFdzJvSPE1v_bD5VcG6w'


class BaseAppHandler(webapp.RequestHandler):
  def get(self):
    pass

  def render_template(self, template_file, template_values):
    template_path = '%s/%s' % (TEMPLATE_DIRS, template_file)
    self.response.headers['Content-Type'] = 'text/html'
    self.response.out.write(template.render(template_path, template_values))

  def basic_template_content(self):
    if '?' in self.request.uri:
      (request_path, querystring) = self.request.uri.split('?')
    else:
      request_path = self.request.uri
    user_info = 'anonymous'
    if users.get_current_user():
      user_info = users.get_current_user().nickname()
    user_info = user_info + ' via ' + self.user_agent_for_display()
    if users.get_current_user():
      url = users.create_logout_url(request_path)
      url_text = 'log out'
    else:
      url = users.create_login_url(request_path)
      url_text = 'log in'
    values = {'user_info': user_info, 'url': url, 'url_text': url_text,
              'maps_api': self.maps_api_url()}
    return values

  def get_user_status(self):
    if users.get_current_user():
      status = {'status': 'logged in'}
    else:
      status = {'status': 'not logged in'}
    return self.output_json(status)

  def user_agent_for_display(self):
    agent = self.request.headers['User-Agent']
    if 'Android' in agent:
      return 'android'
    if 'iPad' in agent:
      return 'ios'
    return 'web'

  def output_json(self, values, xssi=False):
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

    xssi_prefix = ''
    if xssi:
      xssi_prefix = JSON_XSSI_PREFIX

    output = '%s%s' % (xssi_prefix, json.dumps(values))
    self.response.out.write(output)

  def maps_api_url(self):
    server = self.request.headers.get('host', 'no host')
    if (
      server.startswith('www.placingliterature') or
      server.startswith('placingliterature')
    ):
      return GM3_API_URL + '&key=' + GM3_API_KEY
    else:
      return GM3_API_URL
