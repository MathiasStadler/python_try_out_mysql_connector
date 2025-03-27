from __future__ import print_function
from mysql.connector import errorcode

import logging

import time
import mysql.connector

DB_NAME = 'portfolio'




# e.g.
# https://dev.mysql.com/doc/connector-python/en/connector-python-example-ddl.html

TABLES = {}
TABLES['positions'] = (
    "CREATE TABLE `position` ("
    " `no` int NOT NULL AUTO_INCREMENT,"
    " `contract` enum('STK','OPT') NOT NULL,"
    " `strike` DECIMAL(6, 6) NOT NULL,"
    "  PRIMARY KEY (`no`)"
    ") ENGINE=InnoDB")

TABLES['positions_temp2'] = (
    "CREATE TABLE `position` ("
    " `no` int NOT NULL AUTO_INCREMENT,"
    " `contract` enum('STK','OPT') NOT NULL,"
    " `strike` DECIMAL(6, 6) NOT NULL,"
    "  PRIMARY KEY (`no`)"
    ") ENGINE=InnoDB") 

TABLES['positions_temp'] = (
    "CREATE TABLE `position` ("
    " `no` int NOT NULL AUTO_INCREMENT,"
    "  PRIMARY KEY (`no`)"
    ") ENGINE=InnoDB")

# Option(
# conId=763248479,
# symbol='WSM', 
# lastTradeDateOrContractMonth='20250417', 
# strike=150.0, 
# right='P', 
# multiplier='100', 
# primaryExchange='AMEX', 
# currency='USD', 
# localSymbol='WSM   250417P00150000', 
# tradingClass='WSM')
# ]

TABLES['options'] = (
    "CREATE TABLE `options` ("
    " `no` int NOT NULL AUTO_INCREMENT,"
  #  " `conId` int NOT NULL,"
  #  " `symbol` varchar(8) NOT NULL,"
  #  " `lastTradeDateOrContractMonth` date NOT NULL,"
  #  " `strike` DECIMAL(6, 6) NOT NULL,"
  #  " `right` enum('C','P') NOT NULL,"
  #  " `multiplier`int NOT NULL,"
  #  " `primaryExchange` varchar(8) NOT NULL,"
  #  " `currency` varchar(3) NOT NULL ,"
  #  " `localSymbol' varchar(8) NOT NULL ,"
  #  " `tradingClass` varchar(8) NOT NULL ,"
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
    # FROM HERE
    # https://stackoverflow.com/questions/20618570/python-logging-formatter-is-there-any-way-to-fix-the-width-of-a-field-and-jus
    formatter = logging.Formatter(
        "%(levelname)8s | %(asctime)s | %(name)s | %(filename)s:%(funcName)25s | Line# %(lineno)s | %(message)s",
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


def db_disconnect(cnx):

    # FROM HERE
    # https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlconnection-shutdown.html
    # Unlike disconnect(), shutdown() closes the client connection 
    # without attempting to send a QUIT command to the server first.
    #  Thus, it will not block if the connection is disrupted 
    # for some reason such as network failure.

    try:
        cnx.shutdown()
       

    except (mysql.connector.Error, IOError) as err:
        log.info(
            "Disconnection/Shutdown connection %s. Retrying (%d/%d)...",
            err,
            attempt,
            attempts-1,
        )


def db_check_available(cnx, database_name):

    log.debug("start")
    if cnx and cnx.is_connected():
        log.info("db is connected")

        with cnx.cursor() as cursor:

            # FROM HERE
            # https://www.w3schools.com/python/python_mysql_create_db.asp
            try:
                # cursor.execute("USE {}".format(DB_NAME))
                # log.info("Database {} does exists.".format(DB_NAME))

                cursor.execute("SHOW DATABASES")

                # check if available
                result = False

                for x in cursor:
                    log.info("Follow database available {}".format(x))
                    if database_name in x:
                        result = True

                # Don't find the database
                return result

            except mysql.connector.Error as err_one:

                if err_one.errno == errorcode.ER_BAD_DB_ERROR:
                    log.error("Database error => {}".format(err_one))
                    # return False
                    # create_database(cursor)
                    # log.info("Database {} created successfully.".format(DB_NAME))
                    # cnx.database = DB_NAME
                else:
                    log.error("Another err_one => {}".format(err_one))
                    exit(1)

            else:
                return True

    log.debug("finished")


def create_database(cnx, db_name):

    with cnx.cursor() as cursor:
        try:
            log.info("create database {}".format(DB_NAME))
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8mb4'".format(db_name))
        except mysql.connector.Error as err:
            print("Failed creating database: {}".format(err))
            exit(1)


def table_check_available(cnx, table_name):
    log.debug("start")
    if cnx and cnx.is_connected():
        log.info("db is connected")

        with cnx.cursor() as cursor:

            # FROM HERE
            # https://www.w3schools.com/python/python_mysql_create_db.asp
            try:
                cursor.execute("USE {}".format(DB_NAME))
                log.info("use database {} ".format(DB_NAME))

                cursor.execute("SHOW TABLES")

                # check if table available
                result = False

                for x in cursor:
                    log.info("Follow table available {}".format(x))
                    if table_name in x:
                        result = True

                # Don't find the database
                return result

            except mysql.connector.Error as err:

                if err.errno == errorcode.ER_BAD_DB_ERROR:
                    log.error("Database error => {}".format(err))
                else:
                    log.error("Another err => {}".format(err))
                    exit(1)

            else:
                return True

    log.debug("finished")


def table_create(cnx, table_name):

    with cnx.cursor() as cursor:

        table_description = TABLES[table_name]
        try:
            log.debug("Creating table {}: ".format(table_name))
            cursor.execute(table_description)
            cnx.commit()
            
            log.info("cursor output start")
            for x in cursor:
                log.info("{}".format(x))
            log.info("cursor output finish")

        except mysql.connector.Error as err_local:
            if err_local.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                log.error(
                    "database table already exists => {} - Check before you are create twice".format(table_name))
            else:
                log.error("Err {}".format(err_local))

        # FROM HERE last entry
        # https://stackoverflow.com/questions/1278705/when-i-catch-an-exception-how-do-i-get-the-type-file-and-line-number
        except Exception as e:
            log.error("An error => {} occurred line:#{}".format(
                e, e.__traceback__.tb_lineno))
        
        # else:
                # print(err_local.msg)


def run():

    try:
        log.info("init mysql connection")
        # config see on start this files
        cnx = connect_mysql_server_local(config)

        # log.info("check db => {}".format(db_check_available(cnx,DB_NAME)))
        result = db_check_available(cnx, DB_NAME)
        log.info("database available => {}".format(result))

        if result:
            log.info("Database already available")
        else:
            log.info("Database => {} NOT available".format(DB_NAME))
            # create it now
            create_database(cnx, DB_NAME)

        table_name = "positions"

        # result = table_check_available(cnx, "portfolio")
        result = table_check_available(cnx, table_name)

        if result:
            log.info("Table available => {}".format(result))
        else:
            log.info("Table not available => create it now ;-)")
            
            # crete table
            result = table_create(cnx, table_name)

            if result:
                 log.info("Table available => {}".format(result))
            else:
                log.info("Table create result {}".format(result))

        # next table 
        table_name = "options"
        result = table_check_available(cnx, table_name)

        if result:
            log.info("Table available => {}".format(result))
        else:
            log.info("Table not available => create it now ;-)")
            table_create(cnx, table_name)
 
        if result:
            log.info("Table available => {}".format(result))
        else:
            log.info("Table not available => create it now ;-)")
            table_create(cnx, table_name)

        # db_disconnect(cnx)

    # FROM HERE last entry
    # https://stackoverflow.com/questions/1278705/when-i-catch-an-exception-how-do-i-get-the-type-file-and-line-number
    except Exception as e:
        log.error("An error => {} occurred line:#{}".format(
            e, e.__traceback__.tb_lineno))

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
