# import json
import logging

from google.appengine.ext import deferred
from google.appengine.ext import db

from classes import placedlit
from classes import books
# from classes import authors

BATCH_SIZE = 100  # ideal batch size may vary based on entity size.


def transform_author_name_for_query(name):
  """ author id is formatted last_first """
  if ' ' in name:
    first, last = name.rsplit(' ', 1)
    query_name = (last + ' ' + first).lower().replace(' ', '_')
  else:
    query_name = name.lower()
  return query_name


def update_book_data(cursor=None, num_updated=0):
  """ Set ISBNdb reference for places """
  query = placedlit.PlacedLit.all()
  if cursor:
    query.with_cursor(cursor)

  to_put = []
  for place in query.fetch(limit=BATCH_SIZE):
    place.ug_isbn = ''
    place.ISBNdb = None
    query_title = place.title.lower().replace(' ', '_')
    query_author = transform_author_name_for_query(place.author)
    logging.info('%s by %s?', query_title, query_author)
    matching_books = books.Book.get_by_key_name(query_title)
    if matching_books:
      for index, book in enumerate(matching_books.authors):
        author_name = matching_books.authors[index].name()
        if author_name == query_author:
          place.book_data = matching_books
          # to_put.append(place)
          logging.info('found %s by %s', query_title, query_author)
    to_put.append(place)

  if to_put:
    db.put(to_put)
    num_updated += len(to_put)
    logging.debug(
      'Put %d entities to Datastore for a total of %d',
      len(to_put), num_updated)
    deferred.defer(
      update_schema, cursor=query.cursor(), num_updated=num_updated)
  else:
    logging.debug('UpdateSchema complete with %d updates!', num_updated)


def update_user_isbns(cursor=None, num_updated=0):
  """ insert values for user generated isbns """
  query = placedlit.PlacedLit.get_all_unresolved_places()
  if cursor:
    query.with_cursor(cursor)
  unresolved = query.fetch(limit=BATCH_SIZE)

  to_update = []
  titles_isbns = dict()
  places_to_resolve = list(unresolved)
  for index, place in places_to_resolve:
    if place.ug_isbn:
      titles_isbns[place.title] = place.ug_isbn
      places_to_resolve.remove(places_to_resolve[index])
    else:
      to_update.append(place)

  to_put = []
  for place in to_update:
    place.ug_isbn = titles_isbns[place.title]
    to_put.append(place)

  if to_put:
    db.put(to_put)
    num_updated += len(to_put)
    logging.debug(
      'Put %d entities to Datastore for a total of %d',
      len(to_put), num_updated)
    deferred.defer(
      update_schema, cursor=query.cursor(), num_updated=num_updated)
  else:
    logging.debug('update isbns complete with %d updates!', num_updated)