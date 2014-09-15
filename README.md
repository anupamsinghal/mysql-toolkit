# MySql utilities

### update-until ###

#### Requires:
* python 2.7+
* [mysql python connector](http://dev.mysql.com/downloads/connector/python/1.2.html)

#### Features
Repeatedly runs a sql query until no rows get modified.
Indicates a time estimate using target param.
Makes sure slaves don't lag too behind.

#### Parameters:

```
./update-until.py -h
Usage: update-until.py [options]

Options:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --log=LOGLEVEL
                        set log level to any of: debug, info, warn, error,
                        critical (default: info)
  -f LOGFILE, --logfile=LOGFILE
                        log to file with this name
  --host=HOST           host to send requests to (default: localhost)
  -P PORT, --port=PORT  port of host to send requests to (default: 3306)
  --db=DB               name of database (default: nitro_staging)
  -u USER, --user=USER  database user (default: percona)
  -p PASSWORD, --password=PASSWORD
                        database password
  -q QUERY, --query=QUERY
                        query to run
  -t TARGET, --target=TARGET
                        row count target to estimate time remaining (default:
                        0)
  -s SLEEP_MS, --sleep_ms=SLEEP_MS
                        num of milliseconds to sleep betweeen queries
                        (default: 2000)
  --slave_lag=SLAVE_LAG
                        num of seconds slave can lag behind (default: 0)
  --execute             make changes if enabled (default: False)
```