# MySql utilities

### update-until ###

#### Requires:
* python 2.7+
* [mysql python connector](http://dev.mysql.com/downloads/connector/python/1.2.html)

#### Features
1) Repeatedly runs a sql query until no rows get modified.
2) Indicates a time estimate if estimate query is specified.
3) Makes sure slaves don't lag too behind.
    [pt-archiver](http://www.percona.com/doc/percona-toolkit/2.1/pt-archiver.html) could be used for the deletion functionality, but it doesn't figure out the replication slaves and track lag automatically (like pt-online-schema-changes (http://www.percona.com/doc/percona-toolkit/2.1/pt-online-schema-change.html), a truly awesome tool).

#### Parameters:

```
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
  -D DB, --db=DB        name of database (default: nitro_staging)
  -u USER, --user=USER  database user (default: percona)
  -p PASSWORD, --password=PASSWORD
                        database password
  -q QUERY, --query=QUERY
                        query to run
  -e ESTIMATE, --estimate=ESTIMATE
                        query to use to estimate time remaining by first
                        computing total rows to compute.  If not set, estimate
                        will not be provided.
  -s SLEEP_MS, --sleep_ms=SLEEP_MS
                        num of milliseconds to sleep betweeen queries
                        (default: 2000)
  --slave_lag=SLAVE_LAG
                        num of seconds slave can lag behind (default: 0)
  --modify              applies for change queries only. makes changes if
                        enabled (default: False)
  --simulate            applies for change queries only. act like changes are
                        being made but don't make any (default: False)
  --no_fks              disable foreign keys (default: False)

```
