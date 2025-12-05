-- V2 - Procedures
-- Author: Mark Purcell (markpurcell@ie.ibm.com)

SET schema '${schema_name}';

-----------------------------------------------------------------------------
-- MOVIES TABLE FUNCTIONS
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ADD_MOVIE(
    IN p_id INTEGER,
    IN p_imdb_id VARCHAR,
    IN p_title VARCHAR,
    IN p_original_title VARCHAR,
    IN p_overview TEXT,
    IN p_release_date DATE,
    IN p_budget BIGINT,
    IN p_revenue BIGINT,
    IN p_runtime DECIMAL,
    IN p_adult BOOLEAN,
    IN p_popularity DECIMAL,
    IN p_vote_average DECIMAL,
    IN p_vote_count INTEGER,
    IN p_status VARCHAR,
    IN p_tagline VARCHAR,
    IN p_original_language VARCHAR,
    IN p_belongs_to_collection TEXT,
    IN p_homepage VARCHAR,
    IN p_poster_path VARCHAR,
    IN p_production_companies TEXT,
    IN p_production_countries TEXT,
    IN p_spoken_languages VARCHAR,
    IN p_video BOOLEAN
) RETURNS VOID
AS $$
BEGIN
    INSERT INTO MOVIES (
        ID, IMDB_ID, TITLE, ORIGINAL_TITLE, OVERVIEW, RELEASE_DATE,
        BUDGET, REVENUE, RUNTIME, ADULT, POPULARITY, VOTE_AVERAGE,
        VOTE_COUNT, STATUS, TAGLINE, ORIGINAL_LANGUAGE, BELONGS_TO_COLLECTION,
        HOMEPAGE, POSTER_PATH, PRODUCTION_COMPANIES, PRODUCTION_COUNTRIES,
        SPOKEN_LANGUAGES, VIDEO
    ) VALUES (
        p_id, p_imdb_id, p_title, p_original_title, p_overview, p_release_date,
        p_budget, p_revenue, p_runtime, p_adult, p_popularity, p_vote_average,
        p_vote_count, p_status, p_tagline, p_original_language, p_belongs_to_collection,
        p_homepage, p_poster_path, p_production_companies, p_production_countries,
        p_spoken_languages, p_video
    ) ON CONFLICT (ID) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION GET_MOVIES()
RETURNS TABLE(
    id INTEGER, title VARCHAR, release_date DATE, vote_average DECIMAL, vote_count INTEGER
)
AS $$
    SELECT M.ID, M.TITLE, M.RELEASE_DATE, M.VOTE_AVERAGE, M.VOTE_COUNT 
    FROM MOVIES M
    ORDER BY M.TITLE;
$$ LANGUAGE SQL;

-----------------------------------------------------------------------------
-- GENRES TABLE FUNCTIONS
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ADD_GENRE(IN p_genre_id INTEGER, IN p_name VARCHAR) RETURNS VOID
AS $$
BEGIN
    INSERT INTO GENRES (GENRE_ID, NAME) VALUES (p_genre_id, p_name) ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION GET_GENRES()
RETURNS TABLE(id INTEGER, genre VARCHAR)
AS $$
    SELECT G.GENRE_ID, G.NAME FROM GENRES G ORDER BY G.NAME;
$$ LANGUAGE SQL;

-----------------------------------------------------------------------------
-- MOVIE_GENRES TABLE FUNCTIONS
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ADD_MOVIE_GENRE(IN p_movie_id INTEGER, IN p_genre_id INTEGER) RETURNS VOID
AS $$
BEGIN
    INSERT INTO MOVIE_GENRES (MOVIE_ID, GENRE_ID) VALUES (p_movie_id, p_genre_id) 
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------
-- RATINGS TABLE FUNCTIONS
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ADD_RATING(
    IN p_user_id INTEGER,
    IN p_movie_id INTEGER,
    IN p_rating DECIMAL,
    IN p_timestamp BIGINT
) RETURNS VOID
AS $$
BEGIN
    INSERT INTO RATINGS (USER_ID, MOVIE_ID, RATING, TIMESTAMP) 
    VALUES (p_user_id, p_movie_id, p_rating, p_timestamp)
    ON CONFLICT (USER_ID, MOVIE_ID) DO UPDATE SET
        RATING = EXCLUDED.RATING,
        TIMESTAMP = EXCLUDED.TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------
-- LINKS TABLE FUNCTIONS
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION ADD_LINK(
    IN p_movie_id INTEGER,
    IN p_imdb_id VARCHAR,
    IN p_tmdb_id INTEGER
) RETURNS VOID
AS $$
BEGIN
    INSERT INTO LINKS (MOVIE_ID, IMDB_ID, TMDB_ID) 
    VALUES (p_movie_id, p_imdb_id, p_tmdb_id)
    ON CONFLICT (MOVIE_ID) DO NOTHING;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------------------------------------
-- QUERY FUNCTION
-----------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION GET_AVERAGE_RATING_BY_GENRE(
  IN p_genre_name VARCHAR
) RETURNS TABLE(movie_title VARCHAR, avg_rating DECIMAL)
AS $$
BEGIN
    RETURN QUERY
    SELECT M.TITLE, AVG(R.RATING)::DECIMAL(3,1) as avg_rating
    FROM MOVIES M
    JOIN MOVIE_GENRES MG ON M.ID = MG.MOVIE_ID
    JOIN GENRES G ON MG.GENRE_ID = G.GENRE_ID
    JOIN LINKS L ON M.ID = L.TMDB_ID
    JOIN RATINGS R ON L.MOVIE_ID = R.MOVIE_ID
    WHERE G.NAME = p_genre_name
    GROUP BY M.ID, M.TITLE
    HAVING AVG(R.RATING) >= 3.0
    ORDER BY avg_rating DESC;
END;
$$ LANGUAGE plpgsql;