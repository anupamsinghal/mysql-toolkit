
# hide warnings in MySQLdb module
import warnings
warnings.filterwarnings("ignore", message="the sets module is deprecated")
import mysql.connector as mysql

import logging  # debug, info, warning, error, critical
import os, sys, subprocess, re
import urllib
import smtplib
import pprint
import locale

# ------------------------------------------------------
# Data
# -------

pp = pprint.PrettyPrinter(indent=4)
log = None

# ---------------------------------
#  util methods
# ---------------------------------

def init_logging(loglevel, filename = None):
   """Initializes the logging system."""

   numeric_level = getattr(logging, loglevel.upper(), None)
   if not isinstance(numeric_level, int):
       raise ValueError('Invalid log level (must be one of debug, info, warn, error or critical): %s' % opts.loglevel)
   if filename:
      logging.basicConfig(filename=filename, level=numeric_level, format='%(asctime)s %(levelname)s %(thread)d %(module)s:%(lineno)d %(funcName)s() %(message)s')
   else:
      logging.basicConfig(stream=sys.stdout, level=numeric_level, format='%(levelname)s %(message)s')
   global log
   log = logging.getLogger()
   return log
   
def trace(str = "", newline = True):
   """Prints string."""
   if newline:
      print(str)
   else:
      sys.stdout.write(str)

def fatal(str):
   """Logs a critical message."""
   debug("FATAL: " + str)
   log.critical("FATAL: " + str)
   raise SystemExit(1)

def info(str):
   """Logs an information message."""
   log.info(str)

def debug(str):
   """Logs a debug message."""
   log.debug(str)

def newline(str):
   """Appends a newline."""
   return str + '\n'
   
def run(cmd):
   """Executes a command and returns the response."""
   debug("running cmd: " + cmd)
   ret = os.popen(cmd).read()
   return ret

def passthru(cmd):
   '''if "check_output" not in dir( subprocess ): # duck punch it in!
      def f(*popenargs, **kwargs):
         if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
         process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
         output, unused_err = process.communicate()
         retcode = process.poll()
         if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
               cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd)
         return output
      subprocess.check_output = f'''
   print subprocess.check_output(cmd, shell=True)
   
#hook this up with zookeeper web service 
def getShardsGroups(zookeeperServer, clusterName):
   """Uses the zookeeper web service."""
   f = urllib.urlopen("http://zk02.dev.bunchball.net/zkWeb/zk?zookeeperServer=" + zookeeperServer + "&clusterName=" + clusterName)
   response = f.read()
   return json.loads(response)
   
def http_request(url, params = ""):
   """Makes an http GET request."""

   url = "http://" + url
   debug("Making request to: " + url + "?" + str(params))   
   f = urllib.urlopen(url, params)
   response = f.read()   
   return response


# ------------------------------------------------------
# mysql methods
# -------

def sql_connect(host, db, port=3306, user='mainbun', password='l1festream', autocommit = False):
   """
   Sets up a connection to a MySQL server.
   """

   debug("sql connect  host = " + host + ", port = " + str(port))
   conn = mysql.connect(host=host, db=db, user=user, passwd=password, port=port, autocommit = autocommit)
   return conn

def sql_query(cursor, query, modify = False, simulate = False, output = False, fetchOne = False, fetchAll = True, singleColumnAndRow = False, disable_fks = False):
   """
   Queries a SQL connection and returns the resultset.
   """

   debug("query: " + query)
   if disable_fks:
      cursor.execute("SET foreign_key_checks = 0")
   cursor.execute(query)
#   if disable_fks:
#      cursor.execute("SET foreign_key_checks = 1")

   if modify or simulate:
      rows_modified = cursor.rowcount      
      debug("rows modified: %d" % rows_modified)
      if modify:
         cursor.execute("commit")
      return rows_modified
      
   if fetchOne:
      ret = cursor.fetchone()
   elif fetchAll:
      ret = cursor.fetchall()
   else:
      return cursor

   # debug("returning: " + str(ret))
   rows = list()
   
   for i in range(len(ret)):         
      if output: trace("   " + str(i+1) + ". ", newline = False)
      row = dict()
      for j in range(len(cursor.description)):
         if output: trace(str(cursor.description[j][0]) + "=" + str(ret[i][j]), newline=False)
         if singleColumnAndRow:
            return ret[i][j]
         row[str(cursor.description[j][0])] = ret[i][j]
         if j < len(cursor.description) - 1:
            if output: trace(", ", newline=False)
      if output: trace()
      rows.append(row)

   debug("returning rows: " + str(rows))
   return rows

# use single quotes in query
def run_sql(db, query, options = '-BN'):
   """
   Runs a SQL query using the mysql cli. Use single-quotes in query. 
   """

   options += " -u mainbun -pl1festream" 
   debug("query: " + query)
   command = 'mysql ' + options + ' ' + db + ' -e "' + query + '"'
   debug("running command: "  + command)
   #res = os.popen(command).read()
   p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
   #if p.returncode != 0:
   #   fatal("unable to run query")

   res = p.stdout.read().rstrip()   
   debug("result: '" + res + "'")
   return res

def get_shards(cursor, type = 'userdata'):
   """
   Gets all shards of the type specified.
   """
   # run query
   query = "select s.db_server as server, s.db_name as db, s.db_user as user, s.db_password as password from clusters c, shards s where c.primary_shard_id=s.id and c.type = '%s'" % type

   shards = sql_query(cursor = cursor, query = query)

   # extract port
   for shard in shards:      
      if shard['server'].find(':') > -1:
         (host, port) = shard['server'].split(':')
         shard['host'] = host
         shard['port'] = int(port)
      else:
         shard['host'] = shard['server']
         shard['port'] = 3306

   # de-duplicate

   debug(shards)
   return shards

def get_site_shards(cursor):
   """
   Gets all site shards that are referenced by a minisite.
   """

   # run: select si.api_key, sh.db_server as server, sh.db_name as db, sh.db_user as user, sh.db_password as password from sites si, clusters c, shards sh where si.site_common_cluster_id = c.id and c.primary_shard_id=sh.id
   query = "select si.api_key, sh.db_server as server, sh.db_name as db, sh.db_user as user, sh.db_password as password " \
      " from sites si, clusters c, shards sh where si.site_common_cluster_id = c.id and c.primary_shard_id=sh.id"

   shards = sql_query(cursor = cursor, query = query)

   # extract port
   for shard in shards:      
      if shard['server'].find(':') > -1:
         (host, port) = shard['server'].split(':')
         shard['host'] = host
         shard['port'] = int(port)
      else:
         shard['host'] = shard['server']
         shard['port'] = 3306

   # de-duplicate

   debug(shards)
   return shards


# ------------------------------------------------------
# Misc methods
# -------

def get_elapsed_time(seconds, suffixes=['y','w','d','h','m','s'], add_s=False, separator=' '):
   """
   Takes an amount of seconds and turns it into a human-readable amount of time.
   """
   # the formatted time string to be returned
   if seconds < 1:
      return "0s"

   time = []
 
   # the pieces of time to iterate over (days, hours, minutes, etc)
   # - the first piece in each tuple is the suffix (d, h, w)
   # - the second piece is the length in seconds (a day is 60s * 60m * 24h)
   parts = [(suffixes[0], 60 * 60 * 24 * 7 * 52),
        (suffixes[1], 60 * 60 * 24 * 7),
        (suffixes[2], 60 * 60 * 24),
        (suffixes[3], 60 * 60),
        (suffixes[4], 60),
        (suffixes[5], 1)]
 
   # for each time piece, grab the value and remaining seconds, and add it to
   # the time string
   for suffix, length in parts:
      value = seconds / length
      if value > 0:
         seconds = seconds % length
         time.append('%s%s' % (str(value),
                      (suffix, (suffix, suffix + 's')[value > 1])[add_s]))
      if seconds < 1:
         break
 
   return separator.join(time)


"""
def sendEmail(subject, contentMsg, from_address, to_address):
   msg = MIMEText(contentMsg)   
   msg['Subject'] = subject
   msg['From'] = from_address
   msg['To'] = to_address
   try:
      s = smtplib.SMTP('localhost')
      s.sendmail(me, [you], msg.as_string())
      s.quit()
   except Exception, e:
      fatal("SendMail failed: local smtp server " + e)
"""

def number_format(number):
   locale.setlocale(locale.LC_ALL, '')
   return locale.format('%d', number, 1)

