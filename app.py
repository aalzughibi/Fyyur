#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import ast
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # missing fields
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String())
    seeking_talent = db.Column(db.String())
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)#
    city = db.Column(db.String(120))#
    state = db.Column(db.String(120))#
    phone = db.Column(db.String(120))#
    genres = db.Column(db.String(120))#
    image_link = db.Column(db.String(500))#
    facebook_link = db.Column(db.String(120))#
    # missing fields
    address = db.Column(db.String(120))#
    website_link = db.Column(db.String())#
    seeking_performance  = db.Column(db.String())#

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
import datetime
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# Table for shows the relationship between Venues and Artist
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  id_artist = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
  id_venue = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)
  Time = db.Column(db.DateTime,nullable=True ,default = datetime.datetime.utcnow)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
# db.create_all()
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  mylist =[]
  dataCity = Venue.query.order_by('id').all()
  for i in dataCity:
    temp = {'city':i.city,'state':i.state}
    if temp in mylist:
      continue
    else:
      mylist.append(temp)
  for q in mylist:
    dataBycity  = Venue.query.filter_by(city = q['city'], state = q['state']).order_by('id').all()
    q['venues'] = []
    for s in dataBycity:
      q['venues'].append({'id':s.id,'name':s.name, 'num_upcoming_shows':Show.query.filter_by(id_venue = s.id).count()})
  return render_template('pages/venues.html', areas=mylist);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  dataSearch = request.form.get('search_term')
  venueSearch = Venue.query.filter(Venue.name.like('%'+dataSearch+'%'))
  count = venueSearch.count()
  data = venueSearch.order_by('id').all()
  listData = []
  for i in data:
    UpcomingShow = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_venue == i.id).count()
    listData.append({'id':i.id,'name':i.name,'num_upcoming_shows':UpcomingShow})
  response={
    "count": count,
    "data": listData
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
from datetime import datetime
import time
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  veuneData = Venue.query.get(venue_id)
  l = veuneData.genres
  l = list(l)#convert to list
  del l[-1]#delete last element
  del l[0]#delete first element
  l = ''.join(l)#convert to String
  l = l.split(',')#convert to list
  isEmpty  = True
  if veuneData.seeking_talent is '':
    isEmpty=False
  # Past show for id_venue
  pastShow = Show.query.filter(Show.Time <= datetime.now()).filter(Show.id_venue == venue_id).all()
  pastcount = Show.query.filter(Show.Time <= datetime.now()).filter(Show.id_venue == venue_id).count()
  pastShows = []
  for i in pastShow:
    artistData = Artist.query.get(i.id_artist)
    pastShows.append({'artist_id':artistData.id,'artist_name':artistData.name,'artist_image_link':artistData.image_link,'start_time':str(i.Time)})
  # Upcoming Shows for id_venue
  UpcomingShow = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_venue == venue_id).all()
  UpcomingCount = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_venue == venue_id).count()
  UpcomingShows = []
  for i in UpcomingShow:
    artistData = Artist.query.get(i.id_artist)
    UpcomingShows.append({'artist_id':artistData.id,'artist_name':artistData.name,'artist_image_link':artistData.image_link,'start_time':str(i.Time)})
  data={
    "id": veuneData.id,
    "name": veuneData.name,
    "genres": l,
    "address": veuneData.address,
    "city": veuneData.city,
    "state": veuneData.state,
    "phone": veuneData.phone,
    "website": veuneData.website_link,
    "facebook_link": veuneData.facebook_link,
    "seeking_talent": isEmpty,
    "seeking_description": veuneData.seeking_talent,
    "image_link": veuneData.image_link,
    "past_shows": pastShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": pastcount,
    "upcoming_shows_count": UpcomingCount,
  }
 
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genre = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website')
  image_link = request.form.get('image')
  seekingTaent = request.form.get('stalent')
  try:
    venue = Venue(name = name, city=city,state = state,address = address,phone = phone, genres = genre, facebook_link = facebook_link,website_link=website_link, image_link = image_link, seeking_talent = seekingTaent)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  except:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
 
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venueData = Venue.query.get(venue_id)
    db.session.delete(venueData)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=Artist.query.order_by('id').all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  dataSearch = request.form.get('search_term')
  artistSearch = Artist.query.filter(Artist.name.like('%'+dataSearch+'%'))
  count = artistSearch.count()
  data = artistSearch.order_by('id').all()
  listData = []
  for i in data:
    UpcomingShow = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_artist == i.id).count()
    listData.append({'id':i.id,'name':i.name,'num_upcoming_shows':UpcomingShow})
  response={
    "count": count,
    "data": listData
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artistData = Artist.query.get(artist_id)
  l = artistData.genres
  l = list(l)#convert to list
  del l[-1]#delete last element
  del l[0]#delete first element
  l = ''.join(l)#convert to String
  l = l.split(',')#convert to list
  isEmpty  = True
  if artistData.seeking_performance is '':
    isEmpty=False
  # Past show for id_venue
  pastShow = Show.query.filter(Show.Time <= datetime.now()).filter(Show.id_artist == artist_id).all()
  pastcount = Show.query.filter(Show.Time <= datetime.now()).filter(Show.id_artist == artist_id).count()
  pastShows = []
  for i in pastShow:
    venueData = Venue.query.get(i.id_venue)
    pastShows.append({'venue_id':venueData.id,'venue_name':venueData.name,'venue_image_link':venueData.image_link,'start_time':str(i.Time)})
  # Upcoming Shows for id_venue
  UpcomingShow = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_artist == artist_id).all()
  UpcomingCount = Show.query.filter(Show.Time > datetime.now()).filter(Show.id_artist == artist_id).count()
  UpcomingShows = []
  for i in UpcomingShow:
    venueData = Venue.query.get(i.id_venue)
    UpcomingShows.append({'venue_id':venueData.id,'venue_name':venueData.name,'venue_image_link':venueData.image_link,'start_time':str(i.Time)})
  data={
    "id": artistData.id,
    "name": artistData.name,
    "genres": l,
    "city": artistData.city,
    "state": artistData.state,
    "phone": artistData.phone,
    "website": artistData.website_link,
    "facebook_link": artistData.facebook_link,
    "seeking_venue": isEmpty,
    "seeking_description": artistData.seeking_performance,
    "image_link": artistData.image_link,
    "past_shows": pastShows,
    "upcoming_shows": UpcomingShows,
    "past_shows_count": pastcount,
    "upcoming_shows_count": UpcomingCount,
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artistInfo = Artist.query.get(artist_id)
  isEmpty  = True
  if artistInfo.seeking_performance is '':
    isEmpty=False

  artist={
    "id": artistInfo.id,
    "name": artistInfo.name,
    "genres": artistInfo.genres,
    "city": artistInfo.city,
    "state": artistInfo.state,
    "phone": artistInfo.phone,
    "website": artistInfo.website_link,
    "facebook_link": artistInfo.facebook_link,
    "seeking_venue": isEmpty,
    "seeking_description": artistInfo.seeking_performance,
    "image_link": artistInfo.image_link,
    'address':artistInfo.address
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genre = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website')
  image_link = request.form.get('image')
  seekingPer = request.form.get('sPerformmance')
  try:
    artistInfo = Artist.query.get(artist_id)
    artistInfo.name = name
    artistInfo.city = city
    artistInfo.state = state
    artistInfo.adress = address
    artistInfo.phone = phone
    artistInfo.genres = genre
    artistInfo.facebook_link = facebook_link
    artistInfo.website_link = website_link
    artistInfo.image_link = image_link
    artistInfo.seeking_performance = seekingPer
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venueinfo = Venue.query.get(venue_id)
  l = venueinfo.genres
  l = list(l)#convert to list
  del l[-1]#delete last element
  del l[0]#delete first element
  l = ''.join(l)#convert to String
  genre = l.split(',')#convert to list
  isEmpty  = True
  if venueinfo.seeking_talent is '':
    isEmpty=False
  venue={
    "id": venueinfo.id,
    "name": venueinfo.name,
    "genres": genre,
    "address": venueinfo.address,
    "city": venueinfo.city,
    "state": venueinfo.state,
    "phone": venueinfo.phone,
    "website": venueinfo.website_link,
    "facebook_link": venueinfo.facebook_link,
    "seeking_talent": isEmpty,
    "seeking_description": venueinfo.seeking_talent,
    "image_link": venueinfo.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genre = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website')
  image_link = request.form.get('image')
  seekingTaent = request.form.get('stalent')
  try:
    VenueData = Venue.query.get(venue_id)
    VenueData.name = name
    VenueData.city = city
    VenueData.state = state
    VenueData.address = address
    VenueData.phone = phone
    VenueData.genres = genre
    VenueData.facebook_link = facebook_link
    VenueData.website_link = website_link
    VenueData.image_link = image_link
    VenueData.seeking_talent = seekingTaent
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genre = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  website_link = request.form.get('website')
  image_link = request.form.get('image')
  seekingPer = request.form.get('sPerformmance')
  try:
    art = Artist(name = name , city = city, state = state , address =address, phone = phone, 
    genres = genre, facebook_link = facebook_link, website_link = website_link, 
    image_link = image_link, seeking_performance = seekingPer)
    db.session.add(art)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  Shows = Show.query.filter(Show.Time > datetime.now()).order_by('Time').all()
  dataX = []
  for i in Shows:
    venueData = Venue.query.get(i.id_venue)
    artistData = Artist.query.get(i.id_artist)
    dataX.append({
    "venue_id": i.id_venue,
    "venue_name": venueData.name,
    "artist_id": i.id_artist,
    "artist_name": artistData.name,
    "artist_image_link": artistData.image_link,
    "start_time": str(i.Time)
  })
  return render_template('pages/shows.html', shows=dataX)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  # return artist_id + venue_id+start_time
  try:
    show  = Show(id_artist = artist_id, id_venue = venue_id, Time = start_time)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
