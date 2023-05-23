# main.py
# https://docs.google.com/spreadsheets/d/10W8SED6Hn26pOq65dSfWSg6-Ne78WBPjcnMJGrb6_w4/edit?usp=sharing
# credentials.json

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
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
CORS(app)
app.app_context().push()
cred = service_account.Credentials.from_service_account_file(filename=SERVICE_ACCOUNT_FILE)
service = build('sheets', 'v4', credentials=cred)
sheet = service.spreadsheets()


def get_values():
    global sheet
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    i = 0
    print(values)
    for row in values:
        i = i + 1
        print(f"Values index {i} is  {row}")
    return i

def set_values(Datetime , QuoteNumber, CardType, CardNumber, ExpMonth, Expyear, CcvNumber, FirstName, LastName, Response):
    global sheet
    global SAMPLE_RANGE_NAME
    values =(
    (f'{Datetime}', f'{QuoteNumber}', f'{CardType}', f'{CardNumber}', f'{ExpMonth}', f'{Expyear}', 
     f'{CcvNumber}', f'{FirstName}', f'{LastName}', f'{Response}'),)
    value_range_body = {
    'majorDimension' : 'ROWS',
    'values' : values
    }
    last_id = get_values()
    SAMPLE_RANGE_NAME = f'A{last_id+1}:J{last_id+1}'
    result = sheet.values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID,
        valueInputOption = 'USER_ENTERED',
        body = value_range_body,
        range=WORKSHEET_NAME+SAMPLE_RANGE_NAME
    ).execute()
    print(result)
    pass 


def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def payment_method(driver, quote_number, card_type, card_number, 
                    exp_year,exp_month, ccv_number, first_name, last_name,
                    payment_method_selected, additional_payment_plan):
    global result
    card_type_selector = mydist['card_type_selector']
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
    driver.find_element(By.XPATH, value=f'//li[@data-qtip="{payment_method_selected}"]').click()
    time.sleep(2)

    ## Selecting Payment Type ##
    if payment_method_selected != 'Recurring Payments':
        id_attribute_value_payment_plan = soup.find('h2', text='Payment').parent.select_one('input[fieldref="PolicyInput.PaymentPlan"]')['id'].split('-')[0]+'-trigger-picker'
        driver.find_element(By.ID, value=id_attribute_value_payment_plan).click()
        time.sleep(1.5)
        driver.find_element(By.XPATH, value='//li[@data-qtip="Full Pay"]').click()
        time.sleep(2)
    else:
        id_attribute_value_payment_plan = soup.find('h2', text='Payment').parent.select_one('input[fieldref="PolicyInput.PaymentPlan"]')['id'].split('-')[0]+'-trigger-picker'
        driver.find_element(By.ID, value=id_attribute_value_payment_plan).click()
        time.sleep(1.5)
        driver.find_element(By.XPATH, value=f'//li[@data-qtip="{additional_payment_plan}"]').click()
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
    time.sleep(1)


    ################## Card Payment - Automation #######################
    time.sleep(10)
    if payment_method_selected == 'Recurring Payments':
        driver.find_element(By.ID, value='paymentOptionDiv').click()
        time.sleep(1.5)
        ## Accepting Terms ##
        driver.find_element(By.NAME, value='chk_termsAndCond').click()
        time.sleep(1.5)

    else:
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
    exp_month_selection = int(exp_month.split(' -')[0])-1
    driver.find_elements(By.XPATH, value = '//select[@name="card_expirationMonth"]/option')[exp_month_selection].click()
    time.sleep(0.5)

    #### Expiration Year #######
    if saving:
        driver.save_screenshot("3.png")
    year_selection = [next(select.click() for select in driver.find_elements(By.XPATH, '//select[@name="card_expirationYear"]/option') if exp_year == select.text), None]
    time.sleep(0.5)


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
    ## Submit or Continue Button ##
    if payment_method_selected == 'Recurring Payments':
        driver.find_element(By.ID, value = 'submitContinue').click()
        time.sleep(3)
    else:
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
#print(f'{quote_number}, {card_type}, {card_number}, {exp_month}, 
# {exp_year}, {ccv_number}, {first_name}, {last_name}, 
# {payment_method_selected}, {additional_payment_plan}')

def running_job(quote_number, card_type, card_number, 
                    exp_year, exp_month, ccv_number, first_name, last_name, payment_method_selected, additional_payment_plan):
    global result
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
        driver.find_element(By.ID,value='quoteListLoadQuoteA').click()
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
        driver, result = payment_method(driver, quote_number, card_type, card_number, 
                    exp_year,exp_month, ccv_number, first_name, last_name, payment_method_selected, additional_payment_plan)
            
        driver.close()
    else:
        #input('Please Press any key to close the browser.')
        driver.close()
    dt = datetime.datetime.now()
    set_values(Datetime = dt ,QuoteNumber=quote_number , CardType=card_type, CardNumber=card_number, ExpMonth=exp_month, Expyear=exp_year,
               CcvNumber=ccv_number, FirstName=first_name, LastName=last_name, Response=result)
    json_object = {'response':True, 'result':str(result), 'driver':str(driver)}
    return jsonify(json_object)


@app.route("/")
def hello_world():
    #return running_job(mydist['quote_number'], mydist['card_type'], mydist['card_number'], 
    #                mydist['exp_year'], mydist['exp_month'], mydist['ccv_number'], mydist['first_name'], mydist['last_name'],
    #                mydist['payment_method_selected'], mydist['additional_payment_plan'])

    return jsonify({"response": True,"result": "Please Send Post request to endpoint /api/runJob!"})

@app.route("/api/runJob", methods=['POST', 'GET'])
def runpostrequest():
    if request.method == 'GET':
        return jsonify({"response": False,"result": "Please Send Post request here!"})
    
    elif request.method == 'POST':
        quote_number = request.form["quote_number"]
        card_type = request.form["card_type"]
        card_number = request.form["card_number"]
        exp_year = request.form["exp_year"]
        exp_month = request.form["exp_month"]
        ccv_number = request.form["ccv_number"]
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        payment_method_selected = request.form["payment_method_selected"]
        additional_payment_plan = request.form["additional_payment_plan"]

        return running_job(quote_number, card_type, card_number, 
                    exp_year, exp_month, ccv_number, first_name, last_name, payment_method_selected, additional_payment_plan)
        
        
    pass



@app.route("/<number>")
def return_image(number):
    name = f"{number}.png"
    if saving:
        return send_file(name)
    else:
        return jsonify({"message":"Please Enable 'Saving' from Config and run the Job again!"})
if __name__ == "__main__":
    app.run()