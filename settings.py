import os
from dotenv import load_dotenv
load_dotenv()

APP_HOST = os.environ['SERVER_HOST']
APP_PORT = int(os.environ['SERVER_PORT'])

DB_HOST = os.environ['MONGO_DB_HOST']
DB_PORT = int(os.environ['MONGO_DB_PORT'])
