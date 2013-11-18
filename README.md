# talook
[![Build Status](https://api.travis-ci.org/ashcrow/talook.png)](https://travis-ci.org/ashcrow/talook/)

Single web front end for [jsonstats](https://github.com/tbielawa/jsonstats).


## Features
* Only requires Python (w/ simplejson if 2.4 or 2.5)
* Python 2.4+ compatible
* Simple filesystem based caching
* Access and application logging
* JSON based configuration
* host and environment REST endpoints
* Ajaxy
* Unit tested


## Unittests
Use *nosetests -v* from the main directory to execute unittests.

## Configuration
Configuration of the server is done in JSON and is by default kept in the current directories config.json file.
You can override the location by setting TALOOK_CONFIG_FILE environment variable or using the -c/--config
switch on the all in one server.

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
    "templatedir": "/var/www/talook",
    "cachedir": "/var/cache/talook/",
    "cachetime": {"hours": 1},
    "logdir": "/var/logs/talook/",
    "staticdir": "/srv/www/talook/static/"
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

* **talook_access.log**: Access log similar to apache's access log.
* **talook_app.log**: Application level logging which logs some logic results.


## Running

### Simple
1. Edit the configuration file
2. python server.py --listen 0.0.0.0 --port 8008 --config ./config.json

### In Apache
**TODO**
