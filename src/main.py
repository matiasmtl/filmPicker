from flask import Flask, jsonify, request, render_template
import json
import random
import os

app = Flask(__name__)

def load_movies():
    with open(os.path.join(os.path.dirname(__file__), 'movies.json'), 'r') as file:
        return json.load(file)

def save_movies(movies):
    with open(os.path.join(os.path.dirname(__file__), 'movies.json'), 'w') as file:
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
        movie['watched'] = True
        save_movies(movies)
        return jsonify(movie)
    return jsonify({'error': 'No movies left to watch!'})

@app.route('/add_movie', methods=['POST'])
def add_movie():
    new_movie_title = request.form['title']
    movies = load_movies()
    movies.append({"title": new_movie_title, "watched": False})
    save_movies(movies)
    return jsonify({"message": "Movie added successfully!"})

if __name__ == "__main__":
    app.run(debug=True)