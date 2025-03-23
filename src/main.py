from flask import Flask, jsonify, request, render_template
import json
import random
import os
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
if not TMDB_API_KEY:
    logger.error("TMDB_API_KEY is not set. Please check your .env file.")
else:
    logger.debug(f"TMDB_API_KEY loaded successfully: {TMDB_API_KEY}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# Get the absolute path to the directory containing main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Update file paths to use environment variables
MOVIES_FILE = os.getenv('MOVIES_FILE', os.path.join(BASE_DIR, 'data', 'movies.json'))
TV_SHOWS_FILE = os.getenv('TV_SHOWS_FILE', os.path.join(BASE_DIR, 'data', 'tv_shows.json'))

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"

# Add new TMDB TV endpoint
TMDB_TV_SEARCH_URL = "https://api.themoviedb.org/3/search/tv"

def title_case(s):
    """Convert string to title case, handling special cases and preserving articles"""
    # Skip if string is empty
    if not s:
        return s
        
    # Split into words
    words = s.lower().split()
    
    # Capitalize first and last word always
    words[0] = words[0].capitalize()
    if len(words) > 1:
        words[-1] = words[-1].capitalize()
    
    # Words that should stay lowercase (articles, conjunctions, etc.)
    lowercase_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 
                      'of', 'on', 'or', 'the', 'to', 'with'}
    
    # Capitalize all words except those in lowercase_words
    for i in range(1, len(words)-1):
        if words[i].lower() not in lowercase_words:
            words[i] = words[i].capitalize()
    
    return ' '.join(words)

# Function to load movies from the movies JSON file
def load_movies():
    # Try to load and parse the movies file
    try:
        # Check if the movies file exists
        if not os.path.exists(MOVIES_FILE):
            # If the file doesn't exist, create it with an empty list
            with open(MOVIES_FILE, 'w') as file:
                # Write an empty list as JSON to the new file
                json.dump([], file)
        
        # Open the movies file for reading
        with open(MOVIES_FILE, 'r') as file:
            # Parse and return the JSON contents
            return json.load(file)
    # Handle any errors that occur
    except Exception as e:
        # Print error message and return empty list
        print(f"Error loading movies: {str(e)}")
        # Return empty list if there was an error
        return []

def save_movies(movies):
    try:
        with open(MOVIES_FILE, 'w') as file:
            json.dump(movies, file, indent=4)
    except Exception as e:
        print(f"Error saving movies: {str(e)}")

def load_tv_shows():
    try:
        if not os.path.exists(TV_SHOWS_FILE):
            with open(TV_SHOWS_FILE, 'w') as file:
                json.dump([], file)
        
        with open(TV_SHOWS_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading TV shows: {str(e)}")
        return []

def save_tv_shows(shows):
    try:
        with open(TV_SHOWS_FILE, 'w') as file:
            json.dump(shows, file, indent=4)
    except Exception as e:
        print(f"Error saving TV shows: {str(e)}")

def get_unwatched_movies(movies):
    return [movie for movie in movies if not movie['watched']]

def pick_random_movie(movies):
    unwatched_movies = get_unwatched_movies(movies)
    if not unwatched_movies:
        return None
    return random.choice(unwatched_movies)

def get_movie_details(title):
    try:
        # Format the title for better search results
        formatted_title = title_case(title)
        logger.debug(f"Searching for movie: {formatted_title}")
        
        # Set up headers with Bearer token
        headers = {
            'Authorization': f'Bearer {TMDB_API_KEY}',
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        # Search for the movie
        search_response = requests.get(
            TMDB_SEARCH_URL,
            params={
                'query': formatted_title,
                'language': 'en-US'
            },
            headers=headers  # Add headers here
        )
        search_data = search_response.json()
        logger.debug(f"TMDB API Response: {search_data}")
        
        if search_data.get('results'):
            movie = search_data['results'][0]
            logger.debug(f"Found movie: {movie}")
            
            details = {
                'overview': movie.get('overview'),
                'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None,
                'release_date': movie.get('release_date'),
                'rating': movie.get('vote_average')
            }
            logger.debug(f"Returning details: {details}")
            return details
            
    except Exception as e:
        logger.error(f"Error fetching movie details: {str(e)}")
    return None

# Add function to get TV show details
def get_tv_show_details(title):
    try:
        headers = {
            'Authorization': f'Bearer {TMDB_API_KEY}',
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        # Search for the TV show
        search_response = requests.get(
            TMDB_TV_SEARCH_URL,
            params={
                'query': title,
                'language': 'en-US'
            },
            headers=headers
        )
        search_data = search_response.json()
        logger.debug(f"Search results: {search_data}")
        
        if search_data['results']:
            show = search_data['results'][0]
            show_id = show['id']
            episodes = get_tv_show_episodes(show_id)
            
            return {
                'id': show['id'],  # Add this line to include the show ID
                'overview': show.get('overview', ''),
                'poster_path': f"https://image.tmdb.org/t/p/w500{show['poster_path']}" if show.get('poster_path') else None,
                'first_air_date': show.get('first_air_date', ''),
                'rating': show.get('vote_average', 0),
                'seasons': episodes
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Error fetching TV show details: {str(e)}")
        return None

def get_tv_show_episodes(show_id):
    try:
        headers = {
            'Authorization': f'Bearer {TMDB_API_KEY}',
            'Content-Type': 'application/json;charset=utf-8'
        }
        
        logger.info(f"Fetching series data for show ID: {show_id}")
        series_response = requests.get(
            f"https://api.themoviedb.org/3/tv/{show_id}",
            headers=headers
        )
        series_data = series_response.json()
        
        if 'status_code' in series_data and series_data['status_code'] == 34:
            logger.error(f"TV show not found: {show_id}")
            return []

        logger.info(f"Total seasons found: {series_data.get('number_of_seasons', 0)}")
        seasons = []
        today = datetime.today().date()
        
        for season in range(1, series_data.get('number_of_seasons', 0) + 1):
            logger.info(f"Fetching season {season} data")
            season_response = requests.get(
                f"https://api.themoviedb.org/3/tv/{show_id}/season/{season}",
                headers=headers
            )
            season_data = season_response.json()
            
            if 'episodes' in season_data:
                episodes = []
                for ep in season_data['episodes']:
                    air_date = ep.get('air_date')
                    if air_date:
                        episode_date = datetime.strptime(air_date, '%Y-%m-%d').date()
                        if episode_date <= today:
                            episode = {
                                'episode_number': ep['episode_number'],
                                'name': ep.get('name', f'Episode {ep["episode_number"]}'),
                                'overview': ep.get('overview', ''),
                                'air_date': air_date,
                                'watched': False
                            }
                            episodes.append(episode)
                            logger.debug(f"Added episode: S{season}E{ep['episode_number']} - {ep.get('name')}")
                
                if episodes:
                    season_obj = {
                        'season_number': season,
                        'episode_count': len(episodes),
                        'episodes': sorted(episodes, key=lambda x: x['episode_number'])
                    }
                    seasons.append(season_obj)
                    logger.info(f"Added season {season} with {len(episodes)} episodes")

        return seasons

    except Exception as e:
        logger.error(f"Error fetching TV show episodes: {str(e)}")
        return []

# Update the index route to include TV shows
@app.route('/')
def index():
    movies = load_movies()
    tv_shows = load_tv_shows()
    unwatched_count = sum(1 for movie in movies if not movie['watched'])
    watched_movies = [movie for movie in movies if movie['watched']]
    return render_template('index.html', 
                         unwatched_count=unwatched_count, 
                         watched_movies=watched_movies,
                         tv_shows=tv_shows)

@app.route('/pick_movie', methods=['POST'])
def pick_movie():
    try:
        movies = load_movies()
        movie = pick_random_movie(movies)
        
        if not movie:
            return jsonify({'error': 'No unwatched movies available'})
        
        # Get additional details from TMDB
        tmdb_details = get_movie_details(movie['title'])
        
        response = {
            'title': movie['title'],
            'poster': movie['poster'],  # Use the poster from our JSON
            'year': tmdb_details['release_date'][:4] if tmdb_details and 'release_date' in tmdb_details else None,
            'overview': tmdb_details['overview'] if tmdb_details else None,
            'tmdb_rating': tmdb_details['rating'] if tmdb_details else None
        }
        
        return jsonify(response)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/mark_watched', methods=['POST'])
def mark_watched():
    title = request.form['title']
    movies = load_movies()
    for movie in movies:
        if movie['title'] == title:
            movie['watched'] = True
            save_movies(movies)
            return jsonify({"message": f"'{title}' marked as watched!"})
    return jsonify({"error": "Movie not found"}), 404

@app.route('/add_movie', methods=['POST'])
def add_movie():
    new_movie_title = title_case(request.form['title'])  # Format the title
    movies = load_movies()
    
    # Check if movie already exists
    if any(movie['title'].lower() == new_movie_title.lower() for movie in movies):
        return jsonify({"error": "Movie already exists!"}), 400
    
    movie_details = get_movie_details(new_movie_title)
    logger.debug(f"Movie details received: {movie_details}")
    
    new_movie = {
        "title": new_movie_title,
        "watched": False,
        "rating": 0,
        "poster": None,
        "overview": None,
        "release_date": None,
        "tmdb_rating": None
    }
    
    if movie_details:  # Only update if we got details back
        new_movie.update({
            "poster": movie_details.get('poster'),
            "overview": movie_details.get('overview'),
            "release_date": movie_details.get('release_date'),
            "tmdb_rating": movie_details.get('rating')
        })
    
    movies.append(new_movie)
    save_movies(movies)
    return jsonify({"message": "Movie added successfully!"})

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    title = request.form.get('title')
    rating = int(request.form.get('rating'))
    
    if not title or not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({'success': False, 'error': 'Invalid input'}), 400
    
    movies = load_movies()
    for movie in movies:
        if movie['title'] == title:
            movie['rating'] = rating
            save_movies(movies)
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Movie not found'}), 404

# Update add_show route to include show details
@app.route('/add_show', methods=['POST'])
def add_show():
    title = request.form.get('title')
    if not title:
        return jsonify({'success': False, 'error': 'Title is required'})
    
    title = title_case(title)
    
    shows = load_tv_shows()
    if any(show['title'] == title for show in shows):
        return jsonify({'success': False, 'error': 'Show already exists'})
    
    show_details = get_tv_show_details(title)
    if not show_details:
        return jsonify({'success': False, 'error': 'Could not fetch show details'})
        
    new_show = {
        'title': title,
        'status': 'to_watch',
        'rating': 0,
        'overview': show_details.get('overview'),
        'poster': show_details.get('poster_path'),
        'year': show_details.get('first_air_date', '')[:4] if show_details.get('first_air_date') else None,
        'tmdb_id': show_details.get('id'),
        'tmdb_rating': show_details.get('rating'),
        'seasons': get_tv_show_episodes(show_details.get('id'))
    }
    
    shows.append(new_show)
    save_tv_shows(shows)
    return jsonify({'success': True})

@app.route('/rate_show', methods=['POST'])
def rate_show():
    title = request.form.get('title')
    rating = int(request.form.get('rating'))
    
    shows = load_tv_shows()
    for show in shows:
        if show['title'] == title:
            show['rating'] = rating
            save_tv_shows(shows)
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Show not found'})

@app.route('/update_show_status', methods=['POST'])
def update_show_status():
    title = request.form.get('title')
    new_status = request.form.get('status')
    
    if not title or not new_status:
        return jsonify({'success': False, 'error': 'Missing title or status'})
        
    try:
        shows = load_tv_shows()
            
        for show in shows:
            if show['title'].lower() == title.lower():
                prev_status = show.get('status')
                show['status'] = new_status
                
                # When starting to watch, refresh episodes if they're missing
                if new_status == 'ongoing':
                    if not show.get('seasons') or not any(s.get('episodes') for s in show.get('seasons', [])):
                        logger.info(f"Refreshing episodes for show: {title}")
                        show_details = get_tv_show_details(title)
                        if show_details and show_details.get('seasons'):
                            show['seasons'] = show_details['seasons']
                    # Reset episode watch status
                    for season in show.get('seasons', []):
                        for episode in season.get('episodes', []):
                            episode['watched'] = False
                
        save_tv_shows(shows)
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error updating show {title}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Add new route to update episode watched status
@app.route('/update_episode_status', methods=['POST'])
def update_episode_status():
    title = request.form.get('title')
    season = int(request.form.get('season'))
    episode = int(request.form.get('episode'))
    watched = request.form.get('watched') == 'true'
    
    shows = load_tv_shows()
    for show in shows:
        if show['title'] == title:
            # If marking as watched and show is on hold, move to currently watching
            if watched and show['status'] == 'on_hold':
                logger.info(f"Moving show '{title}' from On Hold to Currently Watching due to watched episode")
                show['status'] = 'ongoing'
                
            for s in show['seasons']:
                if s['season_number'] == season:
                    for ep in s['episodes']:
                        if ep['episode_number'] == episode:
                            ep['watched'] = watched
                            # **Check if all episodes are watched**
                            all_watched = all(
                                ep['watched'] for season in show['seasons'] for ep in season['episodes']
                            )
                            if all_watched:
                                show['new_episodes'] = False
                                logger.info(f"All episodes for '{title}' are watched. 'new_episodes' set to False.")
                            save_tv_shows(shows)
                            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Show/episode not found'}), 404

# Add new route to update batch episode watched status
@app.route('/update_episode_status_batch', methods=['POST'])
def update_episode_status_batch():
    try:
        title = request.form.get('title')
        target_season = int(request.form.get('season'))
        target_episode = int(request.form.get('episode'))
        watched = request.form.get('watched') == 'true'
        
        shows = load_tv_shows()
        for show in shows:
            if show['title'] == title:
                # If marking as watched and show is on hold, move to currently watching
                if watched and show['status'] == 'on_hold':
                    logger.info(f"Moving show '{title}' from On Hold to Currently Watching due to batch watched episodes")
                    show['status'] = 'ongoing'
                    
                updated = False
                for season in show['seasons']:
                    season_num = season['season_number']
                    # For seasons before the target season, mark all episodes
                    if season_num < target_season:
                        for ep in season['episodes']:
                            ep['watched'] = watched
                            updated = True
                    # For the target season, mark episodes up to target_episode
                    elif season_num == target_season:
                        for ep in season['episodes']:
                            if ep['episode_number'] <= target_episode:
                                ep['watched'] = watched
                                updated = True
                    # Don't touch episodes in future seasons
                
                if updated:
                    # **Check if all episodes are watched**
                    all_watched = all(
                        ep['watched'] for season in show['seasons'] for ep in season['episodes']
                    )
                    if all_watched:
                        show['new_episodes'] = False
                        logger.info(f"All episodes for '{title}' are watched. 'new_episodes' set to False.")
                    save_tv_shows(shows)
                    return jsonify({'success': True})
                
        return jsonify({'success': False, 'error': 'Show/season not found'})
    except Exception as e:
        logger.error(f"Error in batch update: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add new route to delete TV shows
@app.route('/delete_show', methods=['POST'])
def delete_show():
    title = request.form.get('title')
    if not title:
        return jsonify({'success': False, 'error': 'Title is required'})
    
    shows = load_tv_shows()
    shows = [show for show in shows if show['title'] != title]
    save_tv_shows(shows)
    return jsonify({'success': True})

# Add this function to pull new episodes for all currently watching shows
@app.route('/pull_new_episodes', methods=['POST'])
def pull_new_episodes():
    try:
        shows = load_tv_shows()
        new_episodes_added = False
        status_changes = []
        today = datetime.today().date()
        
        for show in shows:
            if show['status'] in ['ongoing', 'on_hold']:
                # First get the show ID if it's missing
                show_id = show.get('tmdb_id')
                if not show_id:
                    # Try to get show ID from TMDB
                    show_details = get_tv_show_details(show['title'])
                    if show_details:
                        show_id = show_details['id']
                        show['tmdb_id'] = show_id
                
                if show_id:
                    logger.info(f"\n{'='*50}\nChecking episodes for show: {show['title']} (ID: {show_id})")
                    
                    # Get fresh episodes data from TMDB
                    new_seasons = get_tv_show_episodes(show_id)
                    if new_seasons:
                        # Create dictionaries for better comparison
                        current_episodes = {
                            f"s{s['season_number']}e{e['episode_number']}": e
                            for s in show.get('seasons', [])
                            for e in s.get('episodes', [])
                        }
                        
                        new_episodes = {
                            f"s{s['season_number']}e{e['episode_number']}": e
                            for s in new_seasons
                            for e in s.get('episodes', [])
                        }
                        
                        # Log current state
                        logger.debug(f"Current episodes: {list(current_episodes.keys())}")
                        logger.debug(f"New episodes: {list(new_episodes.keys())}")
                        
                        # Check for new episodes
                        has_new_episodes = bool(new_episodes.keys() - current_episodes.keys())
                        
                        # Find latest episode air date
                        latest_air_date = None
                        for episode in new_episodes.values():
                            if episode.get('air_date'):
                                episode_date = datetime.strptime(episode['air_date'], '%Y-%m-%d').date()
                                if not latest_air_date or episode_date > latest_air_date:
                                    latest_air_date = episode_date
                        
                        # Update show status based on latest episode
                        if latest_air_date:
                            days_since_latest = (today - latest_air_date).days
                            
                            if show['status'] == 'ongoing' and days_since_latest > 30:
                                show['status'] = 'on_hold'
                                status_changes.append({
                                    'show': show['title'],
                                    'from': 'ongoing',
                                    'to': 'on_hold'
                                })
                            elif show['status'] == 'on_hold' and has_new_episodes:
                                show['status'] = 'ongoing'
                                status_changes.append({
                                    'show': show['title'],
                                    'from': 'on_hold',
                                    'to': 'ongoing'
                                })
                        
                        # Update episodes while preserving watch status
                        if has_new_episodes:
                            new_episodes_added = True
                            show['seasons'] = new_seasons
                            for season in show['seasons']:
                                for ep in season['episodes']:
                                    key = f"s{season['season_number']}e{ep['episode_number']}"
                                    if key in current_episodes:
                                        ep['watched'] = current_episodes[key]['watched']
                                    else:
                                        ep['watched'] = False
                                        logger.info(f"Added new episode: {key} - {ep['name']}")
                            # **Set the 'new_episodes' flag to True**
                            show['new_episodes'] = True
                        else:
                            # **Ensure the 'new_episodes' flag is False if no new episodes**
                            show['new_episodes'] = False
        
        if new_episodes_added or status_changes:
            save_tv_shows(shows)
        
        logger.info(f"\nPull complete. New episodes added: {new_episodes_added}")
        if status_changes:
            logger.info("Status changes:")
            for change in status_changes:
                logger.info(f"- {change['show']}: {change['from']} -> {change['to']}")
        logger.info('='*50)
        
        return jsonify({
            'success': True, 
            'new_episodes_added': new_episodes_added,
            'status_changes': status_changes
        })
    except Exception as e:
        logger.error(f"Error pulling new episodes: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/unwatched_episodes', methods=['GET'])
def get_unwatched_episodes():
    try:
        shows = load_tv_shows()
        unwatched_episodes = []
        
        for show in shows:
            # Only include shows that are being watched
            if show['status'] == 'ongoing':
                show_episodes = []
                for season in show.get('seasons', []):
                    for episode in season.get('episodes', []):
                        if not episode.get('watched', False):
                            # Format the episode information
                            episode_info = {
                                'show_title': show['title'],
                                'season': season['season_number'],
                                'episode': episode['episode_number'],
                                'title': episode['name'],
                                'air_date': episode.get('air_date'),
                                'poster': show.get('poster')  # Include show poster if available
                            }
                            show_episodes.append(episode_info)
                
                # Sort episodes by season and episode number
                if show_episodes:
                    show_episodes.sort(key=lambda x: (x['season'], x['episode']))
                    unwatched_episodes.extend(show_episodes)
        
        # Sort all episodes by show title
        unwatched_episodes.sort(key=lambda x: x['show_title'])
        
        return jsonify({
            'success': True,
            'unwatched_count': len(unwatched_episodes),
            'episodes': unwatched_episodes
        })
        
    except Exception as e:
        logger.error(f"Error getting unwatched episodes: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)