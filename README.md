# systats

Single web front end for https://github.com/tbielawa/restfulstatsjson.


## Features
* Only requires Python (w/ simplejson if 2.4 or 2.5)
* Python 2.4+ compatible
* Simple filesystem based caching
* Access and application logging
* JSON based configuration
* host and environment REST endpoints
* Ajaxy


## Unittests
Use *nosetests -v* from the main directory to execute unittests.

## Configuration
Configuration of the server is done in JSON and is kept in the current directories config.json file.

| Name          | Type | Value                                         |
|---------------|------|-----------------------------------------------|
| hosts         | dict | hostname: environment pairs                   |
| endpoint      | str  | Endpoint url to pull json data from with a %s placeholder for hostname |
| templatedir   | str  | Directory which holds the templates directory |
| cachedir      | str  | Full path to the cache directory              |
| cachetime     | dict | kwargs for Python's datetime.timedelta [1](http://docs.python.org/2.6/library/datetime.html#datetime.timedelta) |
| logdir        | str  | Full path to the log directory                |
| staticdir     | str  | Full path to the static files directory       |

### Example Configuration
```json
{
    "hosts": {
        "somehost.example.com": "prod",
        "another.host.example.com": "prod",
        "aqasystem.example.com": "qa",
        "127.0.0.1": "dev"
    },

    "endpoint": "http://%s:8888/stats.json",
    "templatedir": "/srv/www/systats",
    "cachedir": "/srv/www/systats/cache",
    "cachetime": {"hours": 1},
    "logdir": "/var/logs/systats/static",
    "staticdir": "/srv/www/systats"
}
```


## URLS

### /
Index page. What a user will interact with.

### /hosts.json
Returns JSON data listing all configured hosts.

### /envs.json
Returns JSON data listing all configured environments.

### /host/*$HOSTNAME*.json
Returns stats for a specific host in JSON format. Cache is used if available.

### /statict/*$FILENAME*
Returns a static file from the static directory.


## Logging
There are two log file which are produced by a running instance.

* **systats_access.log**: Access log similar to apache's access log.
* **systats_app.log**: Application level logging which logs some logic results.


## Running

### Simple
1. Edit the configuration file
2. python server.py
