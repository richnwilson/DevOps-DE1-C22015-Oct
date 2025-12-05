#!/usr/bin/env bash
#author markpurcell@ie.ibm.com

if [ $# -lt 1 ]; then
    echo "Usage: schema-config.sh <schema name>"
    exit 1
fi

command -v docker >/dev/null 2>&1 || { echo >&2 "Error - package docker required, but not available."; exit 1; }
command -v readlink >/dev/null 2>&1 || { echo >&2 "Error - package readlink required, but not available."; exit 1; }

####################################################################################
#Will need the ip address of the host to route traffic between containers
ARCH=$(arch)
if [ "$ARCH" = "arm64" ]; then
  LOCAL_HOST=$(ipconfig getifaddr en0)
else
  LOCAL_HOST=$(hostname -i)
fi

####################################################################################
## Source a file ($1) but redirct output to another file ($2)
##
func_env() {
  set -x; source $1 > temp.txt 2>&1; set +x; sed 's/+//g' temp.txt > $2; rm temp.txt
}

####################################################################################
#Now load postgres config variables and create .env file

source pg.env
func_env pg.env .env

schema=$1
set -x

####################################################################################


####################################################################################
## Postgres bringup and configure
##

#Start the postgres container
func_postgres() {
  echo "Starting Postgres container"
  # Create a named volume first
  docker volume create postgres-data
  
  docker run \
    --name postgres --restart=always --detach \
    -p $PGPORT:$PGPORT \
    --env POSTGRES_PASSWORD=$PGPASSWORD \
    -v postgres-data:/var/lib/postgresql/data \
    postgres:14-alpine
}

func_postgres_wait() {
  echo "Connecting to Postgres container"
  #Wait until postgres is up and accepting connections
  echo "Waiting for database to start..."
  until docker run \
    --rm \
    --link postgres:pg \
    postgres:14-alpine pg_isready \
    -U $PGUSER \
    -h pg; do sleep 2; done
}

#Configure a schema - 1 param (migrate/clean)
func_postgres_config() {
  echo "Applying Postgres schema migrations"
  docker run \
    --rm \
    --link postgres:postgres \
    -v "$(pwd)/db_movies":/flyway/sql \
    flyway/flyway:latest \
    -url=jdbc:postgresql://postgres:$PGPORT/$PGDATABASE \
    -user=$PGUSER -password=$PGPASSWORD \
    -placeholders.schema_name=$schema -cleanDisabled=false -schemas=$schema $1
}
####################################################################################


####################################################################################
## Now run the required functions
##

#Run PostGres
func_postgres

func_postgres_wait

# Remove an existing schema
func_postgres_config clean

#Install the schema
func_postgres_config migrate

