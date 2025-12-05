#!/usr/bin/env python
# author markpurcell@ie.ibm.com

import logging
import postgres as postgres

LOGGER = logging.getLogger(__package__)


class MovieSchema:
    def __init__(self, schema: str):
        self.schema = schema
        if not self.schema:
            raise Exception("No schema specified.")

        self.driver = postgres.PostgresSQLDriver(self.schema)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.driver.close()

    def call_proc(self, procedure, results=True, to_lower=True, params=None):
        return self.driver.call_proc(procedure, results, to_lower, params)

    ####### T2 PROJECT METHODS
    
    # MOVIES TABLE METHODS
    def movie_create(self, movie_data):
        """Insert movie data into MOVIES table"""
        return self.call_proc(
            f"{self.schema}.ADD_MOVIE", 
            results=False, 
            params=(
                movie_data.get('id'),
                movie_data.get('imdb_id'),
                movie_data.get('title'),
                movie_data.get('original_title'),
                movie_data.get('overview'),
                movie_data.get('release_date'),
                movie_data.get('budget'),
                movie_data.get('revenue'),
                movie_data.get('runtime'),
                movie_data.get('adult'),
                movie_data.get('popularity'),
                movie_data.get('vote_average'),
                movie_data.get('vote_count'),
                movie_data.get('status'),
                movie_data.get('tagline'),
                movie_data.get('original_language'),
                movie_data.get('belongs_to_collection'),
                movie_data.get('homepage'),
                movie_data.get('poster_path'),
                movie_data.get('production_companies'),
                movie_data.get('production_countries'),
                movie_data.get('spoken_languages'),
                movie_data.get('video')
            )
        )
    
    def movie_listing(self):
        """Get all movies"""
        return self.call_proc(f"{self.schema}.GET_MOVIES")
    
    # GENRES TABLE METHODS
    def genre_create(self, genre_id: int, name: str):
        """Insert genre into GENRES table"""
        return self.call_proc(
            f"{self.schema}.ADD_GENRE", 
            results=False, 
            params=(genre_id, name)
        )

    def genre_listing(self):
        """Get all genres"""
        return self.call_proc(f"{self.schema}.GET_GENRES")
    
    # MOVIE_GENRES TABLE METHODS
    def movie_genre_create(self, movie_id: int, genre_id: int):
        """Link movie to genre"""
        return self.call_proc(
            f"{self.schema}.ADD_MOVIE_GENRE", 
            results=False, 
            params=(movie_id, genre_id)
        )
    
    # RATINGS TABLE METHODS
    def rating_create(self, user_id: int, movie_id: int, rating: float, timestamp: int):
        """Insert rating into RATINGS table"""
        return self.call_proc(
            f"{self.schema}.ADD_RATING", 
            results=False, 
            params=(user_id, movie_id, rating, timestamp)
        )
    
    # LINKS TABLE METHODS
    def link_create(self, movie_id: int, imdb_id: str, tmdb_id: int):
        """Insert link into LINKS table"""
        return self.call_proc(
            f"{self.schema}.ADD_LINK", 
            results=False, 
            params=(movie_id, imdb_id, tmdb_id)
        )
    
    # QUERY METHODS
    def get_average_rating_by_genre(self, genre_name: str):
        """Get movies with average rating >= 3.0 for a specific genre"""
        return self.call_proc(
            f"{self.schema}.GET_AVERAGE_RATING_BY_GENRE", 
            params=(genre_name,)
        )
