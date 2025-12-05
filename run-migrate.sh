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

#Configure a schema - 1 param (migrate/clean)
func_postgres_config() {
  docker run \
    --rm \
    -v $(readlink -f ./db_movies):/flyway/sql \
    flyway/flyway:latest \
    -url=jdbc:postgresql://$PGHOST:$PGPORT/$PGDATABASE \
    -user=$PGUSER -password=$PGPASSWORD \
    -placeholders.schema_name=$schema -cleanDisabled=false -schemas=$schema $1
}
####################################################################################


####################################################################################
## Now run the required functions
##

#Install the schema
func_postgres_config migrate

