#!/usr/bin/env python
#
# Runs an update query on the specified database while rows are getting changed.
#
# CHANGELOG
#   computes target rows to estimate time
#   added total elapsed time after each tick
#   added total rows modified
#   makes sure slaves don't lag too behind

import sys
import time
import httplib
import urllib
from utils import *

def parse_args():
   """Parses arguments"""
   import optparse

   p = optparse.OptionParser()
   p.add_option("-l", "--log", dest="loglevel", help="set log level to any of: debug, info, warn, error, critical (default: %default)")
   p.add_option("-f", "--logfile", dest="logfile", help="log to file with this name")
   p.add_option("--host", dest="host", help="host to send requests to (default: %default)")
   p.add_option("-P", "--port", dest="port", help="port of host to send requests to (default: %default)")
   p.add_option("-D", "--db", dest="db", help="name of database (default: %default)")
   p.add_option("-u", "--user", dest="user", help="database user (default: %default)")
   p.add_option("-p", "--password", dest="password", help="database password")
   p.add_option("-q", "--query", dest="query", help="query to run")
   p.add_option("-e", "--estimate", dest="estimate", help="query to use to estimate time remaining by first computing total rows to compute.  If not set, estimate will not be provided.")
   p.add_option("-s", "--sleep_ms", dest="sleep_ms", help="num of milliseconds to sleep betweeen queries (default: %default)")
   p.add_option("--slave_lag", dest="slave_lag", help="num of seconds slave can lag behind (default: %default)")
   p.add_option("--modify", action="store_true", dest="modify", help="applies for change queries only. makes changes if enabled (default: %default)")
   p.add_option("--simulate", action="store_true", dest="simulate", help="applies for change queries only. act like changes are being made but don't make any (default: %default)")
   p.add_option("--no_fks", action="store_true", dest="fks", help="disable foreign keys (default: %default)")


   # set defaults
   p.set_defaults(loglevel="info", user="percona", password="toolkit", host="localhost",  \
      port=3306, db="nitro_staging", sleep_ms = 2000, slave_lag = 0, modify = False, estimate = False, fks = False, simulate = False)
   (opts, args) = p.parse_args()
   opts.port = int(opts.port)
   opts.slave_lag = int(opts.slave_lag)
   opts.sleep_ms = int(opts.sleep_ms)  
   #trace ("opts: " +  str(opts))
   return opts

def get_slaves(conn):
   query = "show slave hosts"
   rows = sql_query(conn.cursor(), query)
   return rows

def check_lag(conn, opts):
   # compute slave lag
   debug("Checking lag on slaves")
   counter = 0

   # check lag on all slaves
   for slave in get_slaves(conn):
      slave_conn = sql_connect(slave["Host"], opts.db, slave["Port"], opts.user, opts.password)

      # check lag until all clear
      while True:
         rows = sql_query(slave_conn.cursor(), "show slave status")
         lag = rows[0]["Seconds_Behind_Master"]
         if lag > opts.slave_lag:
            trace("WARNING: %s:%d - slave lag %s is higher than %s. waiting ..." % (slave["Host"], slave["Port"], number_format(lag), number_format(opts.slave_lag)))
            time.sleep(5)
         else:
            debug("INFO: %s:%d - slave lag %s is lower than %s." % (slave["Host"], slave["Port"], number_format(lag), number_format(opts.slave_lag)))
            break
      slave_conn.close()


def main():

   opts = parse_args()
   log = init_logging(opts.loglevel, opts.logfile)

   # start profile
   start = time.time()

   # initialize
   conn = sql_connect(opts.host, opts.db, opts.port, opts.user, opts.password)
   counter = total_rows = total_elapsed = target_rows = 0

   check_lag(conn, opts)

   if opts.estimate:
      # compute target
      target_rows = sql_query(conn.cursor(), opts.estimate, singleColumnAndRow = True)
      trace("Rows to process = %s" % number_format(target_rows))

   # query until done
   while True:

      local_start = time.time()
      counter += 1
      num_rows = sql_query(conn.cursor(), opts.query, modify = opts.modify, simulate = opts.simulate, disable_fks = opts.fks)
      total_rows += num_rows
      elapsed = int(time.time() - local_start)
      total_elapsed += elapsed
      net_elapsed = int(time.time() - start)
      trace("%d. %s rows (%s total) in %s (%s total) - overall %s" % \
          (counter, number_format(num_rows), number_format(total_rows), get_elapsed_time(elapsed), \
            get_elapsed_time(total_elapsed), get_elapsed_time(net_elapsed)), False)
      if opts.estimate:
         rows_left = target_rows - total_rows;
         time_left = int((time.time() - start) / total_rows * rows_left)
         if rows_left > 0 and time_left > 0:            
            trace(", time remaining: %s" % (get_elapsed_time(time_left)))
         else:
            trace("")
      else:
         trace("")
      time.sleep(opts.sleep_ms / 1000)
      check_lag(conn, opts)

      if num_rows == 0:
         break

   conn.close()
   #trace("#\t TOTAL TIME: " + get_elapsed_time( int(time.time() - start)))

if __name__ == '__main__':
   main()
else:
   pass
