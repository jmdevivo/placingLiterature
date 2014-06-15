#!/usr/bin/env coffee

$(document).on('ready', ->
  hpCitySearch = ->
    address = gcfield.value
    geocoder = new google.maps.Geocoder()
    geocoder.geocode {'address':address}, (results, status) =>
      if (status == google.maps.GeocoderStatus.OK)
        position = results[0].geometry.location
        lat = position[Object.keys(position)[0]]
        lng = position[Object.keys(position)[1]]
        mapUrl = window.location.protocol + '//' + window.location.host
        # mapUrl += '/map?lat=' + lat + '&lon=' + lng
        mapUrl += '/map/' + lat + ',' + lng
        window.location = mapUrl
      else
        alert("geocode was not successful: " + status)

  hpAuthorSearch = ->
    authorq = authorfield.value
    mapUrl = window.location.protocol + '//' + window.location.host
    mapUrl += '/map/filter/author/' + authorq
    window.location = mapUrl

  hpSuggestAuthors = ->
    author_data = []
    $.ajax
      url: "/places/authors"
      success: (data) ->
        $.each data, (key, value) ->
          author_data.push(value.author.toString())
        $('#authorq').typeahead({source: author_data})


  updateMapLinksWithLocation = (position) ->
    lat = position.coords.latitude
    lng = position.coords.longitude
    $('#hpbuttons').find('a').attr('href', 'map?lat=' + lat + '&lng=' + lng)


  positionError = (error) ->
    console.log('error', error)
    console.log('client ip', window.REMOTE_ADDR)


  updateMapLinksWithUserLocation = ->
    if navigator.geolocation
      navigator.geolocation.getCurrentPosition(
        updateMapLinksWithLocation, positionError)


  updateMapLinksWithUserLocation()
  hpSuggestAuthors()
  recentPlacesView = new PlacingLit.Views.RecentPlaces
  countView = new PlacingLit.Views.Countview
  # mapCanvas = new PlacingLit.Views.MapCanvasView
  # document.querySelector('.carousel').carousel()
  $('.carousel').carousel()
  gcfield = document.getElementById('gcf')
  gcfield.addEventListener 'keydown', (event) =>
    if (event.which == 13 || event.keyCode == 13)
      event.preventDefault()
      hpCitySearch()
  authorfield = document.getElementById('authorq')
  authorfield.addEventListener 'keydown', (event) =>
    if (event.which == 13 || event.keyCode == 13)
      event.preventDefault()
      hpAuthorSearch()
)
