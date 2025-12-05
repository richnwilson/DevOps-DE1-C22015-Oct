#!/usr/bin/env python3
# author markpurcell@ie.ibm.com

import pandas as pd
import json
import ast
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import movschema
import sys

load_dotenv()

if len(sys.argv) > 1:
    testData = sys.argv[1].lower() != "false"
else:
    print("Pass parameter true to load test data, or false to load all data (will take hours)")


def clean_data_value(value, data_type="str"):
    """Clean and convert data values, handling NaN and invalid data"""
    if pd.isna(value) or value == '' or value == 'NaN':
        if data_type == "int":
            return None
        elif data_type == "float":
            return None
        elif data_type == "bool":
            return False
        else:
            return None
    
    if data_type == "int":
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    elif data_type == "float":
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    elif data_type == "bool":
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes')
        return bool(value)
    elif data_type == "date":
        try:
            if isinstance(value, str) and len(value) >= 10:
                return datetime.strptime(value[:10], '%Y-%m-%d').date()
            return None
        except (ValueError, TypeError):
            return None
    
    return str(value) if value is not None else None

def parse_json_field(json_str):
    """Parse JSON string fields from CSV, handling malformed JSON"""
    if pd.isna(json_str) or json_str == '' or json_str == 'NaN':
        return []
    
    try:
        # Try to parse as JSON first
        if isinstance(json_str, str):
            # Replace single quotes with double quotes for JSON parsing
            json_str = json_str.replace("'", '"').replace('None', 'null').replace('False', 'false').replace('True', 'true')
            return json.loads(json_str)
        return json_str
    except (json.JSONDecodeError, ValueError):
        try:
            # Try to evaluate as Python literal
            return ast.literal_eval(json_str)
        except (ValueError, SyntaxError):
            return []

def load_links_data(schema, file_path="data/links.csv"):
    """Load links data first as it's needed to connect movie IDs"""
    print("Loading links data...")
    
    try:
        df_links = pd.read_csv(file_path)
        print(f"Found {len(df_links)} links records")
        
        success_count = 0
        for _, row in tqdm(df_links.iterrows(), total=len(df_links), desc="Loading links"):
            try:
                movie_id = clean_data_value(row['movieId'], "int")
                imdb_id = clean_data_value(row['imdbId'], "str")
                tmdb_id = clean_data_value(row['tmdbId'], "int")
                
                if movie_id:
                    # Format imdb_id properly (add tt prefix if missing)
                    if imdb_id and not imdb_id.startswith('tt'):
                        imdb_id = f"tt{imdb_id.zfill(7)}"
                    
                    schema.link_create(movie_id, imdb_id, tmdb_id)
                    success_count += 1
                    
            except Exception as e:
                print(f"Error loading link row {row['movieId']}: {e}")
                continue
        
        print(f"Successfully loaded {success_count} links")
        
    except Exception as e:
        print(f"Error loading links data: {e}")

def load_movies_data(schema, file_path="data/movies_metadata.csv", limit=None):
    """Load movies metadata"""
    print("Loading movies data...")
    
    try:
        df_movies = pd.read_csv(file_path, low_memory=False)
        if limit:
            df_movies = df_movies.head(limit)
        
        print(f"Found {len(df_movies)} movie records")
        
        # Track genres for later insertion
        all_genres = set()
        movie_genres_relationships = []
        
        success_count = 0
        for _, row in tqdm(df_movies.iterrows(), total=len(df_movies), desc="Loading movies"):
            try:
                # Parse genres JSON
                genres_data = parse_json_field(row['genres'])
                
                # Collect genre information
                for genre in genres_data:
                    if isinstance(genre, dict) and 'id' in genre and 'name' in genre:
                        all_genres.add((genre['id'], genre['name']))
                        movie_genres_relationships.append((clean_data_value(row['id'], "int"), genre['id']))
                
                # Prepare movie data
                movie_data = {
                    'id': clean_data_value(row['id'], "int"),
                    'imdb_id': clean_data_value(row['imdb_id'], "str"),
                    'title': clean_data_value(row['title'], "str"),
                    'original_title': clean_data_value(row['original_title'], "str"),
                    'overview': clean_data_value(row['overview'], "str"),
                    'release_date': clean_data_value(row['release_date'], "date"),
                    'budget': clean_data_value(row['budget'], "int"),
                    'revenue': clean_data_value(row['revenue'], "int"),
                    'runtime': clean_data_value(row['runtime'], "float"),
                    'adult': clean_data_value(row['adult'], "bool"),
                    'popularity': clean_data_value(row['popularity'], "float"),
                    'vote_average': clean_data_value(row['vote_average'], "float"),
                    'vote_count': clean_data_value(row['vote_count'], "int"),
                    'status': clean_data_value(row['status'], "str"),
                    'tagline': clean_data_value(row['tagline'], "str"),
                    'original_language': clean_data_value(row['original_language'], "str"),
                    'belongs_to_collection': clean_data_value(row['belongs_to_collection'], "str"),
                    'homepage': clean_data_value(row['homepage'], "str"),
                    'poster_path': clean_data_value(row['poster_path'], "str"),
                    'production_companies': clean_data_value(row['production_companies'], "str"),
                    'production_countries': clean_data_value(row['production_countries'], "str"),
                    'spoken_languages': clean_data_value(row['spoken_languages'], "str"),
                    'video': clean_data_value(row['video'], "bool")
                }
                
                # Skip if no valid ID
                if not movie_data['id']:
                    continue
                
                schema.movie_create(movie_data)
                success_count += 1
                
            except Exception as e:
                print(f"Error loading movie row {row.get('id', 'unknown')}: {e}")
                continue
        
        print(f"Successfully loaded {success_count} movies")
        
        # Load genres
        print("Loading genres...")
        genre_success = 0
        for genre_id, genre_name in tqdm(all_genres, desc="Loading genres"):
            try:
                schema.genre_create(genre_id, genre_name)
                genre_success += 1
            except Exception as e:
                print(f"Error loading genre {genre_name}: {e}")
        
        print(f"Successfully loaded {genre_success} genres")
        
        # Load movie-genre relationships
        print("Loading movie-genre relationships...")
        relationship_success = 0
        for movie_id, genre_id in tqdm(movie_genres_relationships, desc="Loading relationships"):
            try:
                if movie_id and genre_id:
                    schema.movie_genre_create(movie_id, genre_id)
                    relationship_success += 1
            except Exception as e:
                print(f"Error loading relationship movie {movie_id} - genre {genre_id}: {e}")
        
        print(f"Successfully loaded {relationship_success} movie-genre relationships")
        
    except Exception as e:
        print(f"Error loading movies data: {e}")

def load_ratings_data(schema, file_path="data/ratings.csv", limit=None):
    """Load ratings data"""
    print("Loading ratings data...")
    
    try:
        df_ratings = pd.read_csv(file_path)
        if limit:
            df_ratings = df_ratings.head(limit)
        
        print(f"Found {len(df_ratings)} rating records")
        
        success_count = 0
        for _, row in tqdm(df_ratings.iterrows(), total=len(df_ratings), desc="Loading ratings"):
            try:
                user_id = clean_data_value(row['userId'], "int")
                movie_id = clean_data_value(row['movieId'], "int")
                rating = clean_data_value(row['rating'], "float")
                timestamp = clean_data_value(row['timestamp'], "int")
                
                if user_id and movie_id and rating is not None and timestamp:
                    schema.rating_create(user_id, movie_id, rating, timestamp)
                    success_count += 1
                    
            except Exception as e:
                print(f"Error loading rating row: {e}")
                continue
        
        print(f"Successfully loaded {success_count} ratings")
        
    except Exception as e:
        print(f"Error loading ratings data: {e}")

def main():
    """Main loading function with test limits"""
    print("Starting MovieLens data loading...")
    
    if testData:
        print("Starting TEST MovieLens data loading...")
        # For testing, use smaller limits
        MOVIE_LIMIT = 1000  # Set to None for full dataset
        RATING_LIMIT = 10000  # Set to None for full dataset
        
        with movschema.MovieSchema("t2project") as schema:
            # Load in order: links -> movies -> ratings
            load_links_data(schema)
            load_movies_data(schema, limit=MOVIE_LIMIT)
            load_ratings_data(schema, limit=RATING_LIMIT)
        
        print("🎉 TEST dataset loading finished!")
        print()
        print("💡 To load the complete dataset (all ~26M ratings), pass false as paramter when running this script")
    else:
        print("Starting COMPLETE MovieLens data loading...")
        print("⚠️  WARNING: This will load the entire dataset and may take several hours!")
        print("⚠️  Ensure you have sufficient time and system resources before proceeding.")
        
        with movschema.MovieSchema("t2project") as schema:
            # Load all data without limits
            print("Loading complete dataset...")
            load_links_data(schema)  # ~45K records
            load_movies_data(schema, limit=None)  # ~45K movies
            load_ratings_data(schema, limit=None)  # ~26M ratings
        
        print("🎉 Complete dataset loading finished!")
        print("   - All links loaded")
        print("   - All movies loaded") 
        print("   - All ratings loaded")
        print("   Ready for performance testing with full dataset!")

if __name__ == "__main__":
    main()