from flask import Flask, jsonify, request, render_template
import json
import random
import os
# import secrets
# print(secrets.token_hex(16))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

# Option 1: Use absolute path during development
# MOVIES_FILE = r'C:\myLocalPath\filmPicker\my-python-project\src\movies.json'

# Option 2: Use relative path from current file
# MOVIES_FILE = os.path.join(os.path.dirname(__file__), 'movies.json')
# print(f"Looking for movies.json at: {MOVIES_FILE}")

# Option 3: Use environment variable with fallback (for Docker deployment)
MOVIES_FILE = os.environ.get('MOVIES_FILE', os.path.join(os.path.dirname(__file__), 'movies.json'))

def load_movies():
    # Create the file if it doesn't exist
    if not os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, 'w') as file:
            json.dump([], file)
    with open(MOVIES_FILE, 'r') as file:
        return json.load(file)

def save_movies(movies):
    with open(MOVIES_FILE, 'w') as file:
        json.dump(movies, file, indent=4)

def get_unwatched_movies(movies):
    return [movie for movie in movies if not movie['watched']]

def pick_random_movie(movies):
    unwatched_movies = get_unwatched_movies(movies)
    if not unwatched_movies:
        return None
    return random.choice(unwatched_movies)

@app.route('/')
def index():
    movies = load_movies()
    unwatched_movies = get_unwatched_movies(movies)
    return render_template('index.html', unwatched_count=len(unwatched_movies))

@app.route('/pick_movie', methods=['POST'])
def pick_movie():
    movies = load_movies()
    movie = pick_random_movie(movies)
    if movie:
        return jsonify(movie)
    return jsonify({'error': 'No movies left to watch!'})

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

if __name__ == "__main__":
    app.run(debug=True)