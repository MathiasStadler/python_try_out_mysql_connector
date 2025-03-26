from __future__ import print_function
from mysql.connector import errorcode

import logging

import time
import mysql.connector

DB_NAME = 'portfolio'

TABLES = {}
TABLES['positions'] = (
    "CREATE TABLE `position` ("
    " `no` int(11) NOT NULL AUTO_INCREMENT,"
    " `contract` enum('STK','OPT') NOT NULL,"
    " `strike` long(11) NOT NULL,"
    "  PRIMARY KEY (`no`)"
    ") ENGINE=InnoDB")

# mysql-server config
config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    # 'database': 'mysql',
    'raise_on_warnings': True
}


# logger
def init_logger():

    # Setup logger
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    # formatter = logging.Formatter(
    #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # nice log output
    formatter = logging.Formatter(
        "%(levelname)s | %(asctime)s |%(name)s |%(filename)s:%(funcName)s :Line %(lineno)s| %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    # Log to console
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

    # Also log to a file
    file_handler = logging.FileHandler("portfolio.log")
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)
    log.debug("start")
    log.debug("finished")
    return log


# connect mysql-server
def connect_mysql_server_local(config, attempts=3, delay=2):
    attempt = 1
    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            log.debug("RETURN successful connection")
            return mysql.connector.connect(**config)
        except (mysql.connector.Error, IOError) as err:
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                log.info(
                    "Failed to connect, exiting without a connection: %s", err)
                return None
            log.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts-1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None

def db_check_available(cnx,database_name):
    log.debug("start")
    if cnx and cnx.is_connected():
        log.info("db is connected")

        with cnx.cursor() as cursor:

# FROM HERE
# https://www.w3schools.com/python/python_mysql_create_db.asp
            try:
                cursor.execute("USE {}".format(DB_NAME))
                log.info("Database {} does exists.".format(DB_NAME))

                cursor.execute("SHOW DATABASES")

                for x in cursor:
                    log.info("Follow database available {}").format(x)

            except mysql.connector.Error as err:
                
                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    log.error("Database error => {}".format(err))
                    # return False
                    # create_database(cursor)
                    # log.info("Database {} created successfully.".format(DB_NAME))
                    # cnx.database = DB_NAME
                else:
                    log.error("Another err => {}".format(err))
                    exit(1)

            else:
                return True
            
    log.debug("finished")
    
def run():

    try:
        log.info("init mysql connection")
        # config see on start this files
        cnx = connect_mysql_server_local(config)
        
        # log.info("check db => {}".format(db_check_available(cnx,DB_NAME)))
        db_check_available(cnx,DB_NAME)

    except Exception as e:
        log.error("An error occurred: {}".format(e))
        
    return None


# main
if __name__ == "__main__":

    # https://metana.io/blog/mastering-python-exception-handling-best-practices-for-try-except/

    try:
        log = init_logger()
        log.debug("program call direct")
        log.info("Start Program")
        run()
        log.info("Finish Prg")
        exit(0)
    except Exception as e:
        print(f"An error occurred: {e}")
else:
    print("call as module")
