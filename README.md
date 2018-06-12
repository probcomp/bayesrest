# Overview

## Initial Setup

After cloning this repo, there are five steps to setup bayesrest:
1. Setup nginx-proxy
1. Add to /etc/hosts
1. Create a `.bdb` file
1. Create a config file
1. Start the app

### Setup probcomp/nginx-proxy repo

Follow the instructions at https://github.com/probcomp/nginx-proxy -- nginx-proxy must be running before you can access bayesrest.

### Add /etc/hosts entry (if you don't already have one)
```
echo "127.0.0.1 bayesrest.probcomp.dev" | sudo tee -a /etc/hosts
```

## Running

### create a `.bdb` file
BayesREST requires that you provide it a `.bdb` file for which analysis has already been performed. Rename that file `database.bdb` and place it at the project root.

## Configuration
To get up and running you are required to define a `application.cfg` file [as described in the Flask documentation](http://flask.pocoo.org/docs/0.12/config/).  We have included a template in `application_defaults.cfg`. Valid options are:
- `BDB_FILE`: The filename of the `.bdb` file to issue queries against.
- `LOG_LEVEL`: The log level for the application. Valid options are `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `NOTSET`.
- `FLASK_CORS_LOG_LEVEL`: The log level for the `flask_cors` module.
- `TABLE_NAME`: The table containing the data under analysis.
- `POPULATION_NAME`: The name of the population in your `.bdb` file

### Start the app
```
docker-compose up
```
(Use the --build option if you've made docker changes.)

Service is accessible at `https://bayesrest.probcomp.dev:8443`

## Endpoints

`/heartbeat`
You can call the `/heartbeat` endpoint with a `GET` request to check if the API is operational.  It will responsd with a `200` status code if the API is up and running.

`/table-data`
You can call the `/table-data` endpoint with a `GET` request to receive a JSON object with the data currently stored in the API.  The JSON object has two elements: `'data'` and `'columns'`, both of which are arrays.

`/find-anomalies`
You can call the `/find-anomalies` endpoint with a `POST` request that sends an object with two keys: `'target-column'` and `'context-column'` -- the values associated with these keys must be the exact names of columns as they exist in your .bdb file.
