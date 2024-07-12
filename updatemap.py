import time,random
import pandas as pd
import signal
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome options for headless browsing
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Comment this line to view browser interactions
# chrome_options.add_argument("--window-size=1920x1080")  # Adjust window size to avoid responsive layouts

# Set up the Chrome driver with headless options
service_obj = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service_obj, options=chrome_options)

# Define the page URL
url = 'https://www.google.com/maps/search/construction+company/@52.2312657,20.9754817,14z/data=!4m7!2m6!3m5!1sconstruction+company!2s52.2325,+20.9927!4m2!1d20.9926972!2d52.2325428?entry=ttu'
driver.get(url)

# Allow the page to load
time.sleep(5)

# Initialize lists to store the data
names = []
addresses = []
phone_numbers = []
websites = []
ratings = []
types = []



# Function to save data and exit gracefully
def save_data_and_exit(signal, frame):
    data = {
        'Name': names,
        'Address': addresses,
        'Phone Number': phone_numbers,
        'Website': websites,
        'Rating': ratings,
        'Type':types
         
      
    }
    df = pd.DataFrame(data)
    df.to_csv('scrapped_data.csv', index=False,encoding='utf-8')
    print('Data saved to scrapped.csv')
    print(f'Total records collected: {len(names)}')
    driver.quit()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, save_data_and_exit)

# Function to scroll the specific div with role='feed' until all results are loaded
def scroll_feed_until_end():
    feed_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
    last_height = driver.execute_script("return arguments[0].scrollHeight", feed_div)
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", feed_div)
        time.sleep(3)
        new_height = driver.execute_script("return arguments[0].scrollHeight", feed_div)
        if new_height == last_height:
            break
        last_height = new_height

# Scroll the feed div to load all results
scroll_feed_until_end()

# Function to extract listing information
def extract_listing_info(listing):
    try:
        # Click on the listing
        listing.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde'))
        )
        time.sleep(random.randint(3,5))
        maindiv = driver.find_element(By.CSS_SELECTOR, 'div.bJzME.Hu9e2e.tTVLSc')
        # Extract the name of the company
        try:
            company_name = maindiv.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
            names.append(company_name)
        except:
            names.append("No Name")

        # Extract the address
        try:
            address = maindiv.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').get_attribute('aria-label')
        except:
            address = 'N/A'
        addresses.append(address)

        # Extract the phone number
        try:
            phone_number = maindiv.find_element(By.CSS_SELECTOR, 'button[data-item-id^="phone:tel"]').get_attribute('aria-label')
        except:
            phone_number = 'N/A'
        phone_numbers.append(phone_number)

        # Extract the website
        try:
            website = maindiv.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]').get_attribute('href')
        except:
            website = 'N/A'
        websites.append(website)

        try:
            ratings_elements = maindiv.find_element(By.CSS_SELECTOR,'span.ceNzKf')
            rating = ratings_elements.get_attribute('aria-label')
        except:

            rating = "No Rating"
        ratings.append(rating)

        try:
            typ = maindiv.find_element(By.CSS_SELECTOR,'button.DkEaL').text
        except:
            typ = "N/A"
        types.append(typ)

        

        # Extract the hours


        # Go back to the list
        driver.find_element(By.CSS_SELECTOR, 'button[jsaction="pane.backToList"]').click()
        time.sleep(3)
    except Exception as e:
        print(f"Failed to process a listing: {e}")

# Main scraping loop to continue until interrupted
while True:
    try:
        # Scroll the feed div to load all results
        scroll_feed_until_end()

        # Extract info from each listing
        listings = driver.find_elements(By.CSS_SELECTOR, 'div.Nv2PK.tH5CWc.THOPZb')
        for listing in listings:
            extract_listing_info(listing)
    except Exception as e:
        print(f"Error in main loop: {e}")

    # Save progress periodically
    save_data_and_exit(None, None)
