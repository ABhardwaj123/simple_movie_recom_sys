from copy import deepcopy
from models import ServiceError

class RecommendationService:
    def __init__(self, movies, ratings, history):
        #movie stores id , title , genres(list) , popularity , available
        self._movies = deepcopy(movies)

        #user -> {movie_id , rating}
        self._ratings = deepcopy(ratings)

        #user -> movie_ids(list)
        self._history = deepcopy(history)


        

    def recommend(self, user, limit=10):
        if isinstance(limit , bool) or not isinstance(limit , int) or limit < 1 or limit > 50:
            raise ServiceError(400, "invalid_limit")

        if not isinstance(user , str) or not user.strip():
            raise ServiceError(400, "invalid_user")

        ratings = self._ratings.get(user , {})
        history = self._history.get(user , [])

        #excluded is the set of movie_ids which the user has either watched or rated
        excluded = set(ratings.keys())
        excluded.update(history)

        #quick mapping for finding movie by its id
        movie_by_id = {
            movie["id"]: movie
            for movie in self._movies
        }

        genre_weights = {}

        for movie_id , rating in ratings.items():
            movie = movie_by_id.get(movie_id)

            if movie is None:
                continue

            weight = rating - 3

            #adding weight to each genre and storing it in genre_weights
            for genre in set(movie["genres"]):
                genre_weights[genre] = (
                    genre_weights.get(genre , 0) + weight
                )

        candidates = []

        for movie in self._movies:
            movie_id = movie["id"]

            if movie_id in excluded:
                continue

            if not movie["available"]:
                continue

            #in genre_weights we have have genre : weight
            #so for each genre now we are gathering weight and having a score
            score = sum(
                genre_weights.get(genre, 0)
                for genre in set(movie["genres"])
            )

            candidates.append({
                "id": movie["id"],
                "title": movie["title"],
                "score": score,
                "popularity": movie["popularity"]
            })


        # - means negative values as python sorts in ascending order in default
        candidates.sort(
            key=lambda movie: (
                -movie["score"],
                -movie["popularity"],
                movie["id"]
            )
        )

        return candidates[:limit]
