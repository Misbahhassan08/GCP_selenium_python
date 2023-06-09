from selenium import webdriver

saving = False
showBrowser = False
result = "Successful"

mydist = {
    'quote_number':'QT00002822031',
    'card_type':'visa',
    'card_number':'3566002020360505',
    'exp_month':'7 - July',
    'exp_year':2023,
    'ccv_number':345,
    'first_name':'ALEXA',
    'last_name':'Dune',
    'card_type_selector':1,
    'payment_method_selected': 'Recurring Payments',
    'additional_payment_plan':'RP-Full Pay'
    # 'RP-Twelve Installments'  'RP-Full Pay'
}

# The following options are required to make headless Chrome
# work in a Docker container
options = webdriver.ChromeOptions()
if showBrowser:
    pass 
elif showBrowser == False:
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

#google cloud -----------------------------------

SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID = '10W8SED6Hn26pOq65dSfWSg6-Ne78WBPjcnMJGrb6_w4'
WORKSHEET_NAME = 'logs!'
SAMPLE_RANGE_NAME = 'A:J'

