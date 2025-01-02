from flask import Flask, jsonify, request, render_template
import json
import random
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# Get the absolute path to the directory containing main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Construct the path to movies.json relative to main.py
MOVIES_FILE = os.path.join(BASE_DIR, 'movies.json')
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie"

def load_movies():
    try:
        if not os.path.exists(MOVIES_FILE):
            # If the file doesn't exist, create it with an empty list
            with open(MOVIES_FILE, 'w') as file:
                json.dump([], file)
        
        with open(MOVIES_FILE, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading movies: {str(e)}")
        return []

def save_movies(movies):
    try:
        with open(MOVIES_FILE, 'w') as file:
            json.dump(movies, file, indent=4)
    except Exception as e:
        print(f"Error saving movies: {str(e)}")

def get_unwatched_movies(movies):
    return [movie for movie in movies if not movie['watched']]

def pick_random_movie(movies):
    unwatched_movies = get_unwatched_movies(movies)
    if not unwatched_movies:
        return None
    return random.choice(unwatched_movies)

def get_movie_details(title):
    try:
        # Search for the movie
        search_response = requests.get(
            TMDB_SEARCH_URL,
            params={
                'api_key': TMDB_API_KEY,
                'query': title,
                'language': 'en-US'
            }
        )
        search_data = search_response.json()
        
        if search_data['results']:
            movie = search_data['results'][0]
            return {
                'overview': movie['overview'],
                'poster_path': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie['poster_path'] else None,
                'release_date': movie['release_date'],
                'rating': movie['vote_average']
            }
    except Exception as e:
        print(f"Error fetching movie details: {str(e)}")
    return None

@app.route('/')
def index():
    movies = load_movies()
    unwatched_count = sum(1 for movie in movies if not movie['watched'])
    watched_movies = [movie for movie in movies if movie['watched']]
    return render_template('index.html', unwatched_count=unwatched_count, watched_movies=watched_movies)

@app.route('/pick_movie', methods=['POST'])
def pick_movie():
    try:
        movies = load_movies()
        unwatched_movies = [movie for movie in movies if not movie['watched']]
        
        if not unwatched_movies:
            return jsonify({'error': 'No unwatched movies left!'})
        
        movie = random.choice(unwatched_movies)
        movie_details = get_movie_details(movie['title'])
        
        response = {
            'title': movie['title'],
            'overview': None,
            'poster': None,
            'year': None,
            'tmdb_rating': None
        }
        
        if movie_details:
            response.update({
                'overview': movie_details['overview'],
                'poster': movie_details['poster_path'],
                'year': movie_details['release_date'][:4] if movie_details['release_date'] else None,
                'tmdb_rating': movie_details['rating']
            })
        
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
    new_movie_title = request.form['title']
    movies = load_movies()
    movies.append({"title": new_movie_title, "watched": False})
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

if __name__ == "__main__":
    app.run(debug=True)