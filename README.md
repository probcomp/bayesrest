# Overview

## Initial Setup

### setup probcomp/nginx-proxy repo

Follow the instructions at https://github.com/probcomp/nginx-proxy -- nginx-proxy must be running before you can access bayesrest.

### add /etc/hosts entry (if you don't already have one)
```
echo "127.0.0.1 bayesrest.probcomp.dev" | sudo tee -a /etc/hosts
```

## Running

### create a `.bdb` file
BayesREST requires that you provide it a `.bdb` file for which analysis has already been performed. Rename that file `database.bdb` and place it at the project root.

### start the app
```
docker-compose up
```
(Use the --build option if you've made docker changes.)

Service is accessible at `https://bayesrest.probcomp.dev:8443`

## Configuration
Additional configuration options can be set by defining a `application.cfg` file [as described in the Flask documentation](http://flask.pocoo.org/docs/0.12/config/). Valid options are:
- `BDB_FILE`: The filename of the `.bdb` file to issue queries against.
- `LOG_LEVEL`: The log level for the application. Valid options are `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`, and `NOTSET`.
- `FLASK_CORS_LOG_LEVEL`: The log level for the `flask_cors` module.
