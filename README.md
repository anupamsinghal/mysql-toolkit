# MySql utilities

## Utilities ##
* update-until
* rename-db

## Pre-requisites:
* python 2.7+
* [mysql python connector](http://dev.mysql.com/downloads/connector/python/1.2.html)


### rename-db ###

#### Features
1. Renames a database to a new name, with some error checks.
1. Aborts on triggers by default.  Can delete them with the --drop-triggers flag.
1. Note: views are ignored and not handled at all.

#### Parameters:
```
Usage: rename-db.py [options]

Options:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --log=LOGLEVEL
                        set log level to any of: debug, info, warn, error,
                        critical (default: info)
  -f LOGFILE, --logfile=LOGFILE
                        log to file with this name
  --host=HOST           host to send requests to (default: localhost)
  -P PORT, --port=PORT  port of host to send requests to (default: 3306)
  -u USER, --user=USER  database user (default: percona)
  -p PASSWORD, --password=PASSWORD
                        database password
  --old=OLDDB           name of old database (default: nitro_staging)
  --new=NEWDB           name of new database (default: DELETE_nitro_staging
  --modify              if false, outputs queries. if true, runs them
                        (default: False)
  --drop-triggers       if true, drop triggers. if false, abort (default:
                        False)
```


### update-until ###

#### Features
1. Repeatedly runs a sql query until no rows get modified.
1. Indicates a time estimate if estimate query is specified.
1. Makes sure slaves don't lag too behind.

#### Notes
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
