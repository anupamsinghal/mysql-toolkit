#!/usr/bin/env python
#
# Renames database on same host:port.  Can be a precursor to dropping database.
#
# CHANGELOG
#     handles triggers

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
   p.add_option("-u", "--user", dest="user", help="database user (default: %default)")
   p.add_option("-p", "--password", dest="password", help="database password")
   p.add_option("--old", dest="olddb", help="name of old database (default: %default)")
   p.add_option("--new", dest="newdb", help="name of new database (default: %default")
   p.add_option("--modify", action="store_true", dest="modify", help="if false, outputs queries. if true, runs them (default: %default)")
   p.add_option("--drop-triggers", action="store_true", dest="drop_triggers", help="if true, drop triggers. if false, abort (default: %default)")

   # set defaults
   p.set_defaults(loglevel="info", user="percona", password="toolkit", host="localhost",  \
      port=3306, modify = False, olddb = "nitro_staging", newdb = "DELETE_nitro_staging", drop_triggers = False)
   (opts, args) = p.parse_args()
   opts.port = int(opts.port)

   return opts

def get_tables(conn, db):
   query = "select table_name from information_schema.tables where table_schema='%s';" % db
   rows = sql_query(conn.cursor(), query)
   return rows


def check_triggers(conn, opts):
   rows = sql_query(conn.cursor(), "select trigger_name from information_schema.triggers where trigger_schema='%s'" % opts.olddb)
   if len(rows) > 0:
      if opts.drop_triggers:
         print("-- Dropping %d trigger(s)" % len(rows))
         for row in rows:
            name = row['trigger_name']
            query = "drop trigger %s;" % name
            print query
            if opts.modify:
               sql_query(conn.cursor(), query, fetchAll = False, modify = True)

      else:
         fatal("%d triggers found. Aborting" % len(rows))

def main():

   opts = parse_args()
   log = init_logging(opts.loglevel, opts.logfile)

   trace ("-- opts: " +  str(opts))
   if opts.olddb == opts.newdb:
      fatal("old and new dbs must be different")

   # start profile
   start = time.time()

   # initialize
   conn = sql_connect(opts.host, opts.olddb, opts.port, opts.user, opts.password)

   check_triggers(conn, opts)

   # create new db
   query = "create database if not exists %s;" % opts.newdb
   if opts.modify:
      sql_query(conn.cursor(), query, modify = True, fetchAll = False)
   else:
      print query

   # make sure no tables in new db already
   tables = get_tables(conn, opts.newdb)
   if len(tables) > 0:
      trace("ERROR: there are already %d table(s) in newdb" % len(tables))
      for table in tables:
         print table['table_name']  
      fatal("aborting")

   # rename all tables in old db
   tables = get_tables(conn, opts.olddb)
   print "-- renaming %d tables" % len(tables)
   for table in tables:
      table = table['table_name']
      query = "rename table %s.%s to %s.%s;" % (opts.olddb, table, opts.newdb, table)
      print query
      if opts.modify:
         sql_query(conn.cursor(), query, fetchAll = False, modify = True)

   # drop old db, if no tables
   if opts.modify:
      tables = get_tables(conn, opts.olddb)
      if len(tables) == 0:
         sql_query(conn.cursor(), "drop database %s;" % opts.olddb, modify = True, fetchAll = False)
      else:
         trace("There are still %d table(s) in the old db: %s" % (len(tables), opts.olddb))
         for table in tables:
            print table['table_name']   
   else:
      print "drop database %s;" % opts.olddb


   conn.close()
   #trace("#\t TOTAL TIME: " + get_elapsed_time( int(time.time() - start)))

if __name__ == '__main__':
   main()
else:
   pass
