# main.py

from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from config import *

from flask import Flask, jsonify, send_file, redirect, url_for, request
from flask_cors import CORS, cross_origin

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
#import chromedriver_binary  # Adds chromedriver binary to path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
CORS(app)
app.app_context().push()

result = "Successful"

quote_number = 'QT00002822031'
card_type = 'visa'
card_number = '3566002020360505'
exp_month = '07 - Jul'
exp_year = 2023
ccv_number = 345
first_name = "ALEXA"
last_name = "Dune"
card_type_selector = 1
# The following options are required to make headless Chrome
# work in a Docker container
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument('--disable-extensions')  # Disables Extensions
options.add_argument("--disable-software-rasterizer")  # Disables "Lost UI Shared Context GPU Error on Windows"
options.add_argument("--log-level=3")  # Errors Only
options.add_argument("--incognito")  # Keeps history and logs clear

options.add_argument("--mute_audio")  # No loud surprises!
options.add_argument("--no-gpu")  # Disables gpu-based errors (headless)
options.add_argument('--disable-plugins')  # Disables Extensions

options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("window-size=1800,1400")
# Initialize a new browser


def payment_method(driver):
    global result
    global quote_number
    global card_type
    global card_type_selector
    global card_number
    global exp_month
    global exp_year
    global ccv_number
    global first_name
    global last_name

    ## Scroll Down ##
    for run in range(2):
        html = driver.find_element(By.TAG_NAME, value='html')
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
    
    soup =BeautifulSoup(driver.page_source, 'lxml')
    ## Selecting Payment Method ##
    id_attribute_value_payment_method = soup.find('h2', text='Payment').parent.select_one('input[fieldref="PaymentInput.PaymentType"]')['id'].split('-')[0]+'-trigger-picker'
    driver.find_element(By.ID, value=id_attribute_value_payment_method).click()
    time.sleep(1.5)
    driver.find_element(By.XPATH, value='//li[@data-qtip="One Time Payment"]').click()
    time.sleep(2)

    ## Selecting Payment Type ##
    id_attribute_value_payment_plan = soup.find('h2', text='Payment').parent.select_one('input[fieldref="PolicyInput.PaymentPlan"]')['id'].split('-')[0]+'-trigger-picker'
    driver.find_element(By.ID, value=id_attribute_value_payment_plan).click()
    time.sleep(1.5)
    driver.find_element(By.XPATH, value='//li[@data-qtip="Full Pay"]').click()
    time.sleep(2)


    ## Hit Complete Issuance ##
    driver.find_element(By.LINK_TEXT, value = 'Complete Issuance').click()
    time.sleep(2)
    driver.find_element(By.ID, value='button-1006-btnInnerEl').click()
    time.sleep(2)

    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    iframe_id = soup.find('iframe')['id']

    ## Switching to First Iframe ##
    driver.switch_to.frame(iframe_id)
    time.sleep(0.5)

    ## Switching to Second Iframe ##
    driver.switch_to.frame('epayui')
    time.sleep(0.5)


    ################## Card Payment - Automation #######################
    
    ## Selecting - Pay Current Due ##
    driver.find_element(By.XPATH, value = '//label[@class="radio ng-binding"]').click()
    time.sleep(1)

    ## Selecting Payment Method - Credit/Debit ##
    driver.find_elements(By.XPATH, value = '//select[@id="paymentMethod"]/option')[-1].click()
    time.sleep(1)
    
    ####### Card Type Selector ############## Card Type Selector #######
    if card_type == 'Visa':
        card_type_selector = 1
    elif card_type == 'Mastercard':
        card_type_selector = 2
    elif card_type == 'Discover':
        card_type_selector = 3

    driver.find_elements(By.XPATH, value = '//select[@name="card_type"]/option')[card_type_selector].click()
    time.sleep(1)


    ###### Providing Card Number ########
    driver.find_element(By.ID, value = 'card_number').clear()
    driver.find_element(By.ID, value = 'card_number').send_keys(card_number)
    time.sleep(0.5)

    #### Expiration Month #######
    exp_month_selection = 8#int(exp_month.split(' -')[0])-1
    driver.find_elements(By.XPATH, value = '//select[@name="card_expirationMonth"]/option')[exp_month_selection].click()
    time.sleep(0.5)

    #### Expiration Year #######
    if saving:
        driver.save_screenshot("3.png")
    #year_selection = [next(select.click() for select in driver.find_elements(By.XPATH, '//select[@name="card_expirationYear"]/option') if exp_year == select.text), None]
    #time.sleep(0.5)


    ### ccv_number ## ### ccv_number ##
    driver.find_element(By.XPATH, value = '//input[@id="card_cvn"]').clear()
    driver.find_element(By.XPATH, value = '//input[@id="card_cvn"]').send_keys(ccv_number)
    time.sleep(0.5)

    ### First Name ##
    driver.find_element(By.XPATH, value = '//input[@name="bill_to_forename"]').clear()
    driver.find_element(By.XPATH, value = '//input[@name="bill_to_forename"]').send_keys(first_name)
    time.sleep(0.5)

    ### Last Name ##
    driver.find_element(By.XPATH, value = '//input[@name="bill_to_surname"]').clear()
    driver.find_element(By.XPATH, value = '//input[@name="bill_to_surname"]').send_keys(last_name)
    time.sleep(0.5)

    ### Use Existing Address ##
    driver.find_element(By.XPATH, value = '//input[@name="chk_useShippingAddress"]').click()
    time.sleep(0.5)
    if saving:
        driver.save_screenshot("4.png")
    driver.find_element(By.ID, value = 'submitPayment').click()
    time.sleep(3)

    driver.find_element(By.ID, value='submitConfirm2').click()
    time.sleep(10)
    
    alert_text = '' 
    if saving:
        driver.save_screenshot("5.png")
    alert_text = '' ; [(time.sleep(5), (soup := BeautifulSoup(driver.page_source, 'lxml')), (alert_text := soup.select_one('.alert').text.strip()))[2] for run in range(5) if alert_text != '' or run == 4 ]
    print(alert_text)
    # ## Close the Browser ##
    #closing_browser = input('Please Press any key to close the browser.')
    #driver.close()

    return [driver, alert_text]
## Running The code After Loggin in ##

@app.route("/")
def hello_world():
    global result
    global driver
    global quote_number
    global card_number
    global exp_month
    global exp_year
    global ccv_number
    global first_name
    global last_name
    global options

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),chrome_options=options)
    driver.implicitly_wait(30)
    driver.maximize_window()
    driver.implicitly_wait(30)
    driver.get("https://magic.markelamerican.com/")
    
    driver.find_element(By.XPATH, value='//input[@id="username-inputEl"]').send_keys('bikers')
    time.sleep(1)
    driver.find_element(By.XPATH, value='//input[@id="password-inputEl"]').send_keys('Markel2020!')
    time.sleep(1)
    driver.find_element(By.XPATH, value='//div[@id="home"]').click()
    #### Payment Function #####

    driver.switch_to.default_content()
    policy_available = 1
    # Home #
    driver.find_element(By.ID, value='id_Home').click()
    time.sleep(2)

    ### Search Button ### ### Search Button ###
    driver.find_element(By.ID, value='id_Search').click()
    time.sleep(3)

    ## Providing Quote Number in the Search Bar ##
    driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').clear()
    driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').send_keys(quote_number)
    # driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').send_keys('123')
    time.sleep(2)

    ## Hitting Search Button ##
    driver.find_element(By.XPATH, value= '//div[@id="searchFilterActions"]/a').click()
    time.sleep(5)

    # Clicking on the first result from the result set ## 
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    if soup.select_one('#quoteListLoadQuoteA'):
        print(f'soup.select_one: DRIVER 1: {driver}')
        driver.find_element(By.ID,value='quoteListLoadQuoteA').click()
        
        print(f'soup.select_one: DRIVER 2: {driver}')
        time.sleep(2)
    else:
        policy_available = 0
        print('\nNo policies matching your search were found. If you wish, revise your search criteria and search again.\n')

    if policy_available == 1:
        
        
        driver.find_element(By.LINK_TEXT, value = 'Submission').click()
        time.sleep(2)

        while True:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if 'Complete Issuance' in soup.text:
                if saving:
                    driver.save_screenshot("1.png")
                print('Payment Page Found.')
                break

            else:
                ## Complete Order ## 
                if 'Complete Quote' in soup.text:
                    if saving:
                        driver.save_screenshot("1.png")
                    driver.find_element(By.LINK_TEXT, value = 'Complete Quote').click()
                    time.sleep(2)

                ## Next Button##
                driver.find_element(By.LINK_TEXT, value = 'Next').click()
                if saving:
                    driver.save_screenshot("2.png")
                time.sleep(2)

        # driver.switch_to.default_content()
        driver, result = payment_method(driver)
            
        driver.close()
    else:
        #input('Please Press any key to close the browser.')
        driver.close()
    json_object = {'response':True, 'result':str(result), 'driver':str(driver)}
    return jsonify(json_object)



@app.route("/api/runJob", methods=['POST', 'GET'])
def runpostrequest():
    global result
    global driver
    global quote_number
    global card_number
    global exp_month
    global exp_year
    global ccv_number
    global first_name
    global last_name
    global options
    if request.method == 'GET':
        return jsonify({"response": False,"result": "Plese Send Post request here!"})
    
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),chrome_options=options)
    driver.implicitly_wait(30)
    driver.maximize_window()
    driver.implicitly_wait(30)
    driver.get("https://magic.markelamerican.com/")
    
    driver.find_element(By.XPATH, value='//input[@id="username-inputEl"]').send_keys('bikers')
    time.sleep(1)
    driver.find_element(By.XPATH, value='//input[@id="password-inputEl"]').send_keys('Markel2020!')
    time.sleep(1)
    driver.find_element(By.XPATH, value='//div[@id="home"]').click()
    #### Payment Function #####

    driver.switch_to.default_content()
    policy_available = 1
    # Home #
    driver.find_element(By.ID, value='id_Home').click()
    time.sleep(2)

    ### Search Button ### ### Search Button ###
    driver.find_element(By.ID, value='id_Search').click()
    time.sleep(3)

    ## Providing Quote Number in the Search Bar ##
    driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').clear()
    driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').send_keys(quote_number)
    # driver.find_element(By.XPATH, value= '//input[@id="_keyvalueTextSearch1-inputEl"]').send_keys('123')
    time.sleep(2)

    ## Hitting Search Button ##
    driver.find_element(By.XPATH, value= '//div[@id="searchFilterActions"]/a').click()
    time.sleep(5)

    # Clicking on the first result from the result set ## 
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    if soup.select_one('#quoteListLoadQuoteA'):
        print(f'soup.select_one: DRIVER 1: {driver}')
        driver.find_element(By.ID,value='quoteListLoadQuoteA').click()
        
        print(f'soup.select_one: DRIVER 2: {driver}')
        time.sleep(2)
    else:
        policy_available = 0
        print('\nNo policies matching your search were found. If you wish, revise your search criteria and search again.\n')

    if policy_available == 1:
        
        
        driver.find_element(By.LINK_TEXT, value = 'Submission').click()
        time.sleep(2)

        while True:
            soup = BeautifulSoup(driver.page_source, 'lxml')
            if 'Complete Issuance' in soup.text:
                if saving:
                    driver.save_screenshot("1.png")
                print('Payment Page Found.')
                break

            else:
                ## Complete Order ## 
                if 'Complete Quote' in soup.text:
                    if saving:
                        driver.save_screenshot("1.png")
                    driver.find_element(By.LINK_TEXT, value = 'Complete Quote').click()
                    time.sleep(2)

                ## Next Button##
                driver.find_element(By.LINK_TEXT, value = 'Next').click()
                if saving:
                    driver.save_screenshot("2.png")
                time.sleep(2)

        # driver.switch_to.default_content()
        driver, result = payment_method(driver)
            
        driver.close()
    else:
        #input('Please Press any key to close the browser.')
        driver.close()
    json_object = {'response':True, 'result':str(result), 'driver':str(driver)}
    return jsonify(json_object)



@app.route("/<number>")
def return_image(number):
    name = f"{number}.png"
    if saving:
        return send_file(name)
    else:
        return jsonify({"message":"Please Enable 'Saving' from Config and run the Job again!"})
    pass
#if __name__ == "__main__":
#    app.run()