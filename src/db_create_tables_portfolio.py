from __future__ import print_function

import logging
import time
import mysql.connector

TABLES = {}
TABLES['positions_one'] = (
    "CREATE TABLE `position` ("
    " `no` int(11) NOT NULL AUTO_INCREMENT,"
    " `contract` enum('STK','OPT') NOT NULL,"
    " `strike` long(11) NOT NULL,"
    "  PRIMARY KEY (`no`)"
    ") ENGINE=InnoDB")

TABLES['positions'] = (
    "CREATE TABLE `position` ("
    " `no` int(11) NOT NULL AUTO_INCREMENT,"
    "  PRIMARY KEY (`no`)"
    " ENGINE=InnoDB")

from mysql.connector import errorcode

DB_NAME = 'portfolio'

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

# Also log to a file
file_handler = logging.FileHandler("portfolio.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler) 

def connect_to_mysql(config, attempts=3, delay=2):
    attempt = 1
    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts-1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None
) ENGINE=InnoDB

def create_database(cursor):
    try:
        logger.info("create database {}".format(DB_NAME))
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
#
def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

##



# from myconnection import connect_to_mysql

config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
# 'database': 'mysql',
  'raise_on_warnings': True
}
cnx = connect_to_mysql(config, attempts=3)

if cnx and cnx.is_connected():

    with cnx.cursor() as cursor:
        # cnx.close()

        databases_available = False
        try:
            
            cursor.execute("SHOW DATABASES")
            # cursor.fetchmany()
            for (databases) in cursor:
                print (databases[0])
                if databases[0] == DB_NAME:
                    databases_available = True
                    logger.info("database => {} available => {}".format(DB_NAME,databases_available))
            if databases_available is False:
                create_database(cursor)

        except mysql.connector.Error as err:
            print(err)
            exit(1)
        try:
            iterator = cursor.execute("USE {}".format(DB_NAME))
            # print(iterator)
            # print("Database {} does exists.".format(DB_NAME))
            create_tables(cursor)
            #found here https://www.reddit.com/r/pythonhelp/comments/1gag8ve/mysql_connector_failing_at_connecting_and_does/
            cursor.close()
            cnx.close()
            exit(0)

        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(cursor)
                print("Database {} created successfully.".format(DB_NAME))
                create_tables(cursor)
                cnx.database = DB_NAME
            else:
                print(err)
                exit(1)
                
        #create table inside database
        try:
            iterator = cursor.execute("USE {}".format(DB_NAME))
            print(iterator)
            print("Database {} does exists.".format(DB_NAME))
            #found here https://www.reddit.com/r/pythonhelp/comments/1gag8ve/mysql_connector_failing_at_connecting_and_does/
            cursor.close()
            cnx.close()
            exit(0)

        except mysql.connector.Error as err:
            print("Database {} does not exists.".format(DB_NAME))
            if err.errno == errorcode.ER_BAD_DB_ERROR:
                create_database(cursor)
                print("Database {} created successfully.".format(DB_NAME))
                cnx.database = DB_NAME
            else:
                print(err)
                exit(1)

else:
    print("Could not connect")