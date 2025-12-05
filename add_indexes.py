#!/usr/bin/env python
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to database
connection = psycopg2.connect(
    host=os.getenv('PGHOST', 'localhost'),
    port=os.getenv('PGPORT', '5432'),
    database=os.getenv('PGDATABASE', 'postgres'),
    user=os.getenv('PGUSER', 'postgres'),
    password=os.getenv('PGPASSWORD', 'password')
)
connection.autocommit = True
cursor = connection.cursor()

# Set schema
cursor.execute("SET schema 't2project'")

print("Creating performance indexes...")

# Create indexes - one line per index
cursor.execute("CREATE INDEX IDX_RATINGS_MOVIE_ID ON RATINGS(MOVIE_ID)")
cursor.execute("CREATE INDEX IDX_RATINGS_RATING ON RATINGS(RATING)")  
cursor.execute("CREATE INDEX IDX_RATINGS_MOVIE_RATING ON RATINGS(MOVIE_ID, RATING)")
cursor.execute("CREATE INDEX IDX_MOVIE_GENRES_GENRE_ID ON MOVIE_GENRES(GENRE_ID)")
cursor.execute("CREATE INDEX IDX_LINKS_TMDB_ID ON LINKS(TMDB_ID)")
cursor.execute("CREATE INDEX IDX_MOVIES_TITLE ON MOVIES(TITLE)")
cursor.execute("CREATE INDEX IDX_MOVIES_VOTE_AVG ON MOVIES(VOTE_AVERAGE)")

print("✅ All 7 indexes created successfully!")

# Close connection
cursor.close()
connection.close()