#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.headerregistry import Address
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from model import Artist, Show, Venue, db

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
m = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


    # TODO: implement any missing fields, as a database migration using Flask-Migrate


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venues_data = []
  venues_city = Venue.query.distinct(Venue.city, Venue.state).all()
  for x in venues_city:
    venues = Venue.query.filter_by(city=x.city, state=x.state).all()
    city_list = []
    for y in venues:
      city_list.append({'id':y.id, 'name': y.name})
      venues_data.append({
        'city': x.city,
        'state': x.state,
        'venues': city_list
      })
      return render_template('pages/venues.html', areas=venues_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  search_text = '%' + search_term + '%'
  results = Venue.query.filter((Venue.name).ilike(search_text)).all()
  response={
    "count":len(results),
    "data":results
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id\
  data_db = Venue.query.get(venue_id)
  venue_detail = db.session.query(Show, Artist).select_from(Show).join(Artist).filter(Show.venue_id == venue_id and Show.artist_id == Artist.id).all()
  show_venue_result = {
          "id": "",
          "name": "",
          "genres": [],
          "address": "",
          "city": "",
          "state": "",
          "phone": "",
          "website": "",
          "facebook_link": "",
          "seeking_talent": False,
          "image_link": "",
          "past_shows": [],
          "upcoming_shows": [],
          "past_shows_count": 0,
          "upcoming_shows_count": 0,
  }
  show_venue_result['id'] = data_db.id
  show_venue_result['name'] = data_db.name
  show_venue_result['address'] = data_db.address
  show_venue_result['city'] = data_db.city
  show_venue_result['state'] = data_db.state
  show_venue_result['phone'] = data_db.phone
  show_venue_result['facebook_link'] = data_db.facebook_link
  show_venue_result['image_link'] = data_db.image_link
  show_venue_result['website'] = data_db.website_link
  show_venue_result['seeking_description'] = data_db.description

  show_venue_result['seeking_talent'] = str(data_db.seeking_venue).lower() in ['true', '1', 't', 'y', 'yes']


  for gener in data_db.genres:
        show_venue_result['genres'].append(gener)
  for show, artist in venue_detail:
        date_time_record = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        if date_time_record<current_time:
          show_venue_result['past_shows_count'] = show_venue_result['past_shows_count']+1
          show_venue_result['past_shows'].append({
             "artist_id": show.artist_id,
             "artist_name": artist.name,
             "artist_image_link": artist.image_link,
              "start_time": show.start_time
            })

        else:
         show_venue_result['upcoming_shows_count'] = show_venue_result['upcoming_shows_count']+1
         show_venue_result['upcoming_shows'].append({
             "artist_id": show.artist_id,
            "artist_name": artist.name,
             "artist_image_link": artist.image_link,
            "start_time": show.start_time
           })

  
  return render_template('pages/show_venue.html', venue=show_venue_result)

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
  form = VenueForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  seeking_venue = form.seeking_talent.data
  seeking_description = form.seeking_description.data
  gener = form.genres.data     
  website = form.website_link.data
  venue = Venue(name=name,city = city, state = state, address  = address,phone = phone,
      image_link = image_link,facebook_link = facebook_link,website_link = website,
      genres = gener,description = seeking_description,seeking_venue = seeking_venue)
  db.session.add(venue)
  db.session.commit()
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  db.session.delete(venue)
  db.session.commit()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.all()
  data = artists
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  search_text = '%' + search_term + '%'
  results = Artist.query.filter((Artist.name).ilike(search_text)).all()
  response={
    "count":len(results),
    "data":results
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  show_artist_result = {
    "id": "",
    "name": "",
    "genres": [],
    "city": "",
    "state": "",
    "phone": "",
    "seeking_venue": False,
    "website": "",
    "facebook_link": "",
    "image_link": "",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data_db= Artist.query.get(artist_id)
  artist_detail = db.session.query(Show, Venue).select_from(Show).join(Venue).filter(Show.artist_id == artist_id and Show.venue_id == Venue.id).all()


  show_artist_result['id'] = data_db.id
  show_artist_result['name'] = data_db.name
  show_artist_result['city'] = data_db.city
  show_artist_result['state'] = data_db.state
  show_artist_result['phone'] = data_db.phone
  show_artist_result['image_link'] = data_db.image_link
  show_artist_result['website'] = data_db.website_link
  show_artist_result['facebook_link'] = data_db.facebook_link

  show_artist_result['seeking_description'] = data_db.seeking_description
  #show_artist_result['genres'].append(data_db.genres)
  show_artist_result['seeking_venue'] = str(data_db.looking_venue).lower() in ['true', '1', 't', 'y', 'yes']
  #show_artist_result['genres'].append(data_db.genres)
  for gener in data_db.genres:
        show_artist_result['genres'].append(gener)

  for show, venue in artist_detail:
        date_time_record = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        if date_time_record<current_time:
         show_artist_result['past_shows_count'] = show_artist_result['past_shows_count']+1
         show_artist_result['past_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time
            })
        else:
          show_artist_result['upcoming_shows_count'] = show_artist_result['upcoming_shows_count']+1
          show_artist_result['upcoming_shows'].append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
           })
  
  return render_template('pages/show_artist.html', artist=show_artist_result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  edit_artist_detail = Artist.query.get(artist_id)
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=edit_artist_detail)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist_detail = Artist.query.get(artist_id)
  if len(form.name.data)>0:
    artist_detail.name = form.name.data
  if len(form.city.data)>0:
    artist_detail.city = form.city.data
  if len(form.state.data)>0:
    artist_detail.state = form.state.data
  if len(form.phone.data)>0:
    artist_detail.phone = form.phone.data
  if len(form.genres.data)>0:
    artist_detail.genres = form.genres.data
  if len(form.image_link.data)>0:
    artist_detail.image_link = form.image_link.data
  if len(form.facebook_link.data)>0:
    artist_detail.facebook_link = form.facebook_link.data
  if len (form.website_link.data)>0:
    artist_detail.website_link = form.website_link.data
  artist_detail.looking_venue = form.seeking_venue.data
  if len(form.seeking_description.data)>0:
    artist_detail.seeking_description = form.seeking_description.data
  db.session.commit()
  artist_detail = ArtistForm(request.form)
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

 
  # TODO: populate form with values from venue with ID <venue_id>
  venue= Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue = Venue.query.get(venue_id)
  if len(form.name.data)>0:
    venue.name = form.name.data
  if len(form.city.data)>0:
    venue.city = form.city.data
  if len(form.state.data)>0:
    venue.state = form.state.data
  if len(form.address.data)>0:
    venue.address = form.address.data
  if len(form.phone.data)>0:
    venue.phone = form.phone.data
  if len(form.genres.data)>0:
    venue.genres = form.genres.data
  if len(form.image_link.data)>0:
    venue.image_link = form.image_link.data
  if len(form.facebook_link.data)>0:
    venue.facebook_link = form.facebook_link.data
  if len(form.website_link.data)>0:
    venue.website_link = form.website_link.data
  form.looking_talent = form.seeking_talent.data
  if len(form.seeking_description.data)>0:
    venue.seeking_description = form.seeking_description.data
  
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data
  facebook_link = form.facebook_link.data
  website_link = form.website_link.data
  looking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data
  artist = Artist(name=name, city=city, state=state, phone=phone,
     genres=genres, image_link=image_link, facebook_link=facebook_link, 
     website_link=website_link, looking_venue=looking_venue, seeking_description=seeking_description)
  db.session.add(artist)
  db.session.commit()

  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by('id').all()
  data = []
  for show in shows:
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)

    shows_details={
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }
    data.append(shows_details)




  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  form = ShowForm(request.form)
  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  start_time = datetime.strptime(str(form.start_time.data), '%Y-%m-%d %H:%M:%S')
  show_record = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
  db.session.add(show_record)
  db.session.commit()
  
  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
