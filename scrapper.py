from flask import Flask, request, jsonify
from db import init_db, get_db_connection
import requests
from bs4 import BeautifulSoup


app = Flask(__name__)

init_db()


