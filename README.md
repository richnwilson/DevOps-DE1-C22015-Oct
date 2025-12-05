# Data Engineering Engineering Rally

# DE1-C22025-Oct 
To see information on how to execute this solution and an alternative solution we created click [here](#rally)


## Introduction
The goal of this project is to apply the knowledge you acquired in databases during the SE4R course material.

Specifically, you will be asked to create an SQL schema and load a relatively large dataset into it. The goal is to demonstrate that applying an indexing strategy to a regular SQL schema significantly increases the query retrieval speed for large datasets.

As part of these tasks, you will demonstrate your ability to design a schema, load data into a database and perform efficient queries upon this dataset.
Included here, are samples to help you to get started. These samples are based on SQL, but you can use other tools if you wish. For example, you could use a cloud instance of PostgreSQL, instead of the local Docker-based version.


### Submission Procedure
* Please fork this Github Repo and follow the steps below
* To show completion and move to the next specialization, you must complete the survey that is linked in the PPT Template. 
* When completed, please submit your results using the following [Powerpoint template](https://ibm.ent.box.com/integrations/officeonline/openOfficeOnline?fileId=1742736582794&sharedAccessCode=) and place it in the root folder of your forked repo.
  * Keep in mind you will only need to upload only one submission per group. The most important element to include in this presentation consists of a screenshot of your query before and after indexing (see below in Task 5).
  * Tip: consider shutting down and restarting the db server in between the timing tests to make sure nothing is cached.
  * Please also provide information within the powerpoint on contributions from each team member.



## Project Tasks

### Task 0: Setup Project
<!-- 1. Install [PostgreSQL](https://www.postgresql.org/) on your machine. -->
1. Install a package manager of your choice. For MacOS we recommend using [Homebrew](https://brew.sh/)
2. Install a Docker client of your choice (not Docker Desktop which is not approved for use). We recommend using [Colima](https://github.com/abiosoft/colima): `brew install colima`
3. Start your colima docker client `colima start`. Wait a few seconds and verify that it is running doing `docker ps`
4. Create a Python Virtual Environment: `python -m venv venv && source venv/bin/activate`
5. Install the packages in the `requirements.txt` file: `pip install -r requirements.txt`
5.1 If some dependencies fail to install you might have to install a local copy of [PostgreSQL](https://www.postgresql.org/): `brew install postgresql@14`
6. Download the [MovieLens Dataset](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset) inside a new dir named `ROOT_DIR/data` : `mkdir -p data && curl -L -o ./data/the-movies-dataset.zip https://www.kaggle.com/api/v1/datasets/download/rounakbanik/the-movies-dataset && unzip ./data/the-movies-dataset.zip -d ./data && rm ./data/the-movies-dataset.zip`

7. We created a local development script `run-local-env.sh ` to get you started setting up the database server. 
7.1 Before running anything make sure there is no previously running postgres container `docker stop postgres && docker rm postgres`
7.2 Run ```./run-local-env.sh t2project```. 
This will:
    * Install a local PostgreSQL instance (Docker)
    * Create a `.env` file with connection details that is used by the data loaders etc.
    * Create a schema called `t2project` defined in a directory called `db_movies/`
 




### Task 1: Create a Schema for the MovieLens Dataset
In this sample, we use Flyway, to create and migrate database schemas over time. You can use another tool if you wish.

* In the `db_movies/db/migration` you will find 2 starter files. 
  * `V1__Initial_Schema.sql`: defines each table in your database schema. 
  * `V2__Procs.sql`: defines the SQL functions that let you add/retrieve data in your dbj

 1. Populate these 2 files in order to design a schema with as many tables and functions as needed to import the data located in the `movies_metadata.csv` and `ratings.csv` files of the MovieLens dataset (hint you might need to check out the `links.csv` file for corresponding `id/imdb_id/movie_id` columns).
   * **IMPORTANT:** For the moment, do not use any indexes in your schema (you will do so in task 4 below)
 2. Once your schema and SQL functions are ready, run ```./run-local-env.sh t2project```. This will run these `*.sql` files in version (`V__*`) order and setup your DB.

**HINTS:**
* We recommend using SQL directly but you are welcome to use any other tool to create this schema.
* The starter code uses a library called [Flyway](https://www.red-gate.com/products/flyway/), a database migration tool used for versioning and managing database changes. Once `V__*` files are ran by Flyway they shouldn't be changed unless you decide to delete the database. If you ever wish to later change the database schema, all you have to do is add another `V__*` file with a higher number and it'll only run this file and ignore previously ran `V__*` files. In this way, you can effectively migrate a database schema over time, without removing the underlying data that is already stored in the database.


### Task 2: Load the MovieLense Dataset 
Now that you have your SQL schema and functions setup, it's time to populate this DB with the dataset. 

* We have created starter Python scripts for you `run_load_data_movies.py` and `movschema.py` which let you connect to the DB and call functions defined in your `V2__Procs.sql` file.
1. Complete these two Python scripts accordingly in order to load the data located in both the `movies_metadata.csv` and `ratings.csv` files in the schema you created in the previous task. You can ignore other files in the dataset.

**HINT:**
* Datasets always contain inconsistencies in their data types (NaNs etc.). This dataset unfortunately is no exception, hence you will probably have to clean the dataset (checking data types inconsistencies etc. ) before being able to load it in the DB.
* Loading the full dataset will take a few hours. We recommend testing the schema beforehand on a smaller subset of the data.


### Task 3: Query the Database
Now that you have loaded the dataset into your database, it's time to make some queries.

* We have created a starter Python script `run_query.py`. 

1. Try and come up with a query sophisticated enough which will require a significant amount of time to retrieve. The query should be run for all the genres available in the dataset. An example query could be: `"Select all the movies that have an average user rating of >= 3 stars AND are of the genre science fiction."`
2. Measure the time taken by the query to retrieve the data requested per genre. And calculate the `total retrieval time` required for all genres.

**HINTS:**
* You can use the [SQL AVG](https://www.w3schools.com/sql/sql_avg.asp) function to calculate the average of a DB column


### Task 4: Add an Index to your schema
Well done, you've created a full insertion and retrieval database cycle. Now is the time to increase the efficiency of your retrieval step.

1. Modify the original schema created in Task 1, in order to add an index on tables which you feel could speed up the retrieval process of the query you produced in Task 3.


**HINTS:**
* You can use the [SQL INDEX](https://www.w3schools.com/sql/sql_create_index.asp) keyword to create indexes
* You can "migrate" the initial schema by adding additional `V__*` files as per the Flyway migration process.


### Task 5: Re-run the queries with an index
Now that you have improved your initial schema with an index, it's time to see if this helps improve the retrieval time.

1. Re-run the queries created in Task 3 and compare the total retrieval time. You should see a significant decrease in time required to retrieve the data. If this isn't the case, try and come up with a more sophisticated query in Task 3 or an improved indexing strategy.


### Results
In order to complete this project, please provide:
1. A link to your Github repository 
2. A screenshot of retrieval times of your query WITH AND WITHOUT using an index in your schema


## Steps to replicate (assuming all pre-requiste libraries are installed) <a name="rally"></a> 
0. `chmod +x *.py` and then `chmod +x *.sh`
1. `colima start`
2. `docker ps`
3. `python3 -m venv venv && source venv/bin/activate`
4. `pip3 install -r requirements.txt`
5. `./downloadData.sh`
6. `docker pull postgres:14-alpine`
7. `docker pull flyway/flyway:latest`
8. `./run-local-env.sh t2project`
9. If using smaller test data, `./run_load_data_movies.py true`, otherwise for all data `./run_load_data_movies.py false`
   ![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/3d50376a-7fab-47a2-a5ce-4aa55456a81f)

11. `./run_query.py PRE "Science Fiction"`
![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/abdb389c-62ab-46d8-9ec6-cfc569ec0cf5)
 
13. `./add_indexes.py`
    ![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/27a259d1-8cf4-489e-ae90-e53196d3e5ce)

14. `./run_query.py POST "Science Fiction"`
 ![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/edf7d35d-0e23-43e7-b5e5-2c6ffbfd1454)


16. `./stopPostgresql.sh`
17. `colima stop`

### Re-starting build
1. `./stopPostgresql.sh`
2. `colima stop`
3. `colima start`
4. `./run-local-env.sh t2project`
5. If using smaller test data, `./run_load_data_movies.py true`, otherwise for all data `./run_load_data_movies.py false`

### Results

#### Test data:
 - PRE INDEX QUERY -- for genre 'Science Fiction' - Query executed in 0.0156 seconds.
 - POST INDEX QUERY -- for genre 'Science Fiction' - Query executed in 0.0129 seconds.
 
### Full data:
 - PRE INDEX QUERY -- for genre 'Science Fiction' - 1340 results - Query executed in 3.8167 seconds.
 - POST INDEX QUERY -- for genre 'Science Fiction' - 1340 results - Query executed in 1.1174 seconds.


# Alternative solution (using Google Colab and Gemini AI)
Out of curiosity, we also decided to try and create the entire solution in Google Colab using Google Gemini.
This turned out to be a pretty fast and efficient solution (although for time purposes, we only worked with a subset of the data)
The link to the solution is available [here](https://colab.research.google.com/drive/12-gezQzBV6TTxH_hOmjRQYco7aqJN3NT?usp=sharing)

Here are the screenshots with timings before and after indexing:
### Before
![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/9705b878-ea67-4365-892f-f8111fbe299a)

### After
![image](https://github.ibm.com/rwilson/DE1-C22025-Oct/assets/162683/f0a760fc-652e-4bc1-aab6-eb54d8022a67)
