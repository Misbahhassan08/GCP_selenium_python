from selenium import webdriver

saving = False
result = "Successful"

mydist = {
    'quote_number':'QT00002822031',
    'card_type':'visa',
    'card_number':'3566002020360505',
    'exp_month':'07 - Jul',
    'exp_year':2023,
    'ccv_number':345,
    'first_name':'ALEXA',
    'last_name':'Dune',
    'card_type_selector':1
}

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