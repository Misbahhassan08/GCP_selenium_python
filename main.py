# main.py

from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_binary  # Adds chromedriver binary to path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
CORS(app)
app.app_context().push()

quote_number = 4453
card_type = 'visa'
card_number = '3566002020360505'
exp_month = 'jan'
exp_year = 2023
ccv_number = 345
first_name = "ALEXA"
last_name = "Dune"
# The following options are required to make headless Chrome
# work in a Docker container
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize a new browser
browser = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)


@app.route("/")
def hello_world():
    browser.get("https://www.google.com/search?q=headless+horseman&tbm=isch")
    json_object = {'response':True, 'driver':str(browser)}
    return jsonify(json_object) 
