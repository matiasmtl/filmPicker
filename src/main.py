import json
import random
import time
import os

def load_movies():
    with open(os.path.join(os.path.dirname(__file__), 'movies.json'), 'r') as file:
        return json.load(file)

def save_movies(movies):
    with open(os.path.join(os.path.dirname(__file__), 'movies.json'), 'w') as file:
        json.dump(movies, file, indent=4)

def get_unwatched_movies(movies):
    return [movie for movie in movies['movies'] if not movie['watched']]

def pick_random_movie(movies):
    unwatched_movies = get_unwatched_movies(movies)
    if not unwatched_movies:
        return None
    return random.choice(unwatched_movies)

def main():
    movies = load_movies()
    unwatched_movies = get_unwatched_movies(movies)
    print(f"Want to watch a movie tonight? You have {len(unwatched_movies)} movies remaining in your 2025 must watch list. Answer Yes or No")
    answer = input().strip().lower()

    if answer == "no":
        print("Okay. Let me know if you change your mind.")
        time.sleep(3)
        return

    while answer == "yes":
        movie = pick_random_movie(movies)
        if movie is None:
            print("No movies left to watch in the 2025 list!")
            break
        print(f"How about watching '{movie['title']}'?")
        movie['watched'] = True
        save_movies(movies)
        time.sleep(5)
        print("Do you want to watch another one? Answer Yes or No")
        answer = input().strip().lower()

    print("Alright, until next time!")
    time.sleep(3)

if __name__ == "__main__":
    main()