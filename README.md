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

## Queries you can run using the Bayesian Database Search API

The Bayesian Database Search API can run three main queries at present:
* Find Anomalies
* Find Similar Rows
* Find Dependent Columns

You might be asking yourself "when would I want to use these queries?"  To answer this question let's illustrate how each of these queries would work within the context of a fictitious dataset.  Lets say this dataset has 10,000 rows, each of which is a person, and four columns: person_id, age, max_running_speed, and favorite color.  Let's see what our queries could do with a datset like this.

### Find Anomalies

Let's say that you'd like to find - of all 10,000 people - which person stands out the most in terms of their `max_running_speed`, or in other words is "anomalous" in terms of their running speed.  How would you do this?

Well, one way you might go about this is to take the average max running speed of all people in your list and find the person who is furthest from this average on either end.  Make sense?  This probably isn't a revolutionary technique to you.

But now let's say that we'd like to find a person stands out in terms of their running speed, given their age.  How might we figure this out?  Well, problems like these - referred to as a multivariate problem - can be difficult, especially as they increase in their complexity.  And this is where the "Find Anomalies" query of the Bayesian Database Search API can be helpful.  It lets you indicate which column you'd like to "search for anomalousness", and which column(s) you'd like to take into consideration as context (in this example, age), and - voila - suddenly you have a way of spotting the 100 year old marathon runner and 5 year old future track star.

### Find Similar Rows

Now let's say there is a certain person in this list who is of interest to you for one reason or another, and you'd like to find more people like this.  To be specific in our example, let's say this person has the following characteristics:

* `person_id`: 12931249
* `age`: 14
* `max_running_speed`: 13 (mph)
* `favorite_color`: blue

(And, for context, the world record running speed is 27.8 mph, set by Usain Bolt in the 100 meter sprint in August of 2009.)

So, we have a fairly average (in terms of `max_running_speed`) `14` year old whose favorite color is `blue`, and we'd like to find more people like this.  Within the context of the constrained set of columns this might be pretty easy.  We could use filters in a spreadsheet to filter out people with these characteristics or construct a SQL query with `WHERE` statements that specify these exact characteristics.

But now let's imagine we add 300 columns with additional information about each person.  Suddenly our techniques for finding people who are similar get a lot more burdensome.  This is a scenario where our "Find Similar Rows" query can be of help.  It lets you indicate which row is of particular interest to you, and it will send you back a ranking that indicates which rows are most similar to the row you indicated.

### Find Dependent Columns

Ok, now finally let's say that we want to find which columns the `max_running_speed` column appears to depend on the most.  Or, in other words, given the `max_running_speed` of all 10,000 people in our dataset, are there relationships between all of our columns?  For our simple example, we would see a strong relationship between a person's `age` and their `max_running_speed`: generally, we would expect people to get faster in life until somewhere around the age of 21, and then there is a decrease in their maximum running speed over time.  And, on the other hand, we would expect for there to relationship between a person's `favorite_color` and their `max_running_speed`.

Again, in our simple example, one's "gut" might do a pretty good job of identifying these relationships, but as the size and complexity of our data grows, the ability of this API to do this becomes more and more valuable.

### A Summary of the Value of this API

This API is most helpful in analyzing large, messy, multivariate datasets with missing values.  In each of the examples laid out above, the API's ability to provide answers scales with increasing size, complexity, and messiness of our data, which would otherwise require trained data scientists hours of work.

## Endpoints

###`/heartbeat`
You can call the `/heartbeat` endpoint with a `GET` request to check if the API is operational.  It will responsd with a `200` status code if the API is up and running.

###`/table-data`
You can call the `/table-data` endpoint with a `GET` request to receive a JSON object with the data currently stored in the API.

The JSON object has two properties: `'data'` and `'columns'`.  The `'data'` element is an array of arrays, in which each inner array is row of data.  The `'columns'` element is an array of strings -- one for each column name.

###`/find-anomalies`
You can call the `/find-anomalies` endpoint with a `POST` request that sends an object with two keys:
* `'target-column'` - this must be a string equal to one of the column names.
* `'context-columns'` - this must be an array containing one or more strings, each of which being a column name.

You will receive a status code back, indicating whether or not your query was successful.  If it is, you may subsequently hit the `/anomaly-scatterplot-data` endpoint.

###`/anomaly-scatterplot-data`
You can call the `/anomaly-scatterplot-data` endpoint with a `GET` request. You will receive a JSON object back.

###`/find-peers`
You can call the `/find-peers` endpoint with a `POST` request that sends an object with two keys:
* `'target-column'` - this must be a string equal to one of the column names.
* `'context-column'` - this must be a string equal to one of the column names.

You will receieve a status code back, indicating whether or not your query was sucessful.  If it is, you may subsequently hit the `/peer-heatmap-data` endpoint.

###`/peer-heatmap-data`
You can call the `/peer-heatmap-data` endpoint with a `GET` request.  You will receive a JSON object back.


###`/last-query`
You can call the `/last-query` endpoint with a `GET` request.  You will receieve a JSON object back with the following properties:
* `last_query`
* `type`
* `target_column`
* `context_columns`
