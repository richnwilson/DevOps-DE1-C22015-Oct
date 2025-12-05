#!/usr/bin/env python
# author markpurcell@ie.ibm.com
from dotenv import load_dotenv
import movschema
import json
import time
import sys
from decimal import Decimal

if len(sys.argv) > 1:
    state = sys.argv[1]
    genre = sys.argv[2]
else:
    print("Pass parameter of either PRE or POST, then a string for Genre")

def decimal_to_str_encoder(obj):
    """Custom encoder function to handle Decimal types."""
    if isinstance(obj, Decimal):
        # Convert the Decimal to its string representation
        return str(obj)
    # Let the default encoder handle all other types
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

load_dotenv()

schema = movschema.MovieSchema("t2project")

start_time = time.time()
# Select all the movies that have an average user rating of >= 3 stars AND are specified genre
_, _, query = schema.get_average_rating_by_genre(genre)
end_time = time.time()
execution_time = end_time - start_time 

print(json.dumps(query, indent=4, default=decimal_to_str_encoder))
print(f"\n{state} INDEX QUERY -- for genre '{genre}' - {len(query)} results - Query executed in {execution_time:.4f} seconds.")