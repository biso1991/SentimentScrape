import os
import logging
from time import time, sleep
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

key = [
    "MONGO_CHECK_TIMEOUT",
    "MONGO_CHECK_INTERVAL",
    "MONGO_INITDB_DATABASE",
    "MONGO_INITDB_ROOT_USERNAME",
    "MONGO_INITDB_ROOT_PASSWORD",
    "MONGO_HOST",
]
check_timeout = int(os.getenv(key[0], 30))
check_interval = int(os.getenv(key[1], 1))
interval_unit = "second" if check_interval == 1 else "seconds"
config = {
    "database": os.getenv(key[2], "admin"),
    "username": os.getenv(key[3], "mongoadmin"),
    "password": os.getenv(key[4], "mongopass"),
    "host": os.getenv(key[5], "mongodb"),
}

start_time = time()
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def mongo_isready(host, username, password, database):
    uri = f"mongodb://{username}:{password}@{host}:27017/{database}"
    while time() - start_time < check_timeout:
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=check_interval * 1000)
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            logger.info("MongoDB is ready! ✨ 💅")
            client.close()
            return True
        except ServerSelectionTimeoutError:
            logger.info(
                f"MongoDB isn't ready. Waiting for {check_interval} {interval_unit}..."
            )
            sleep(check_interval)
    logger.error(f"We could not connect to MongoDB within {check_timeout} seconds.")
    return False

mongo_isready(**config)