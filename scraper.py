import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException  
from selenium.webdriver.common.action_chains import ActionChains

config = configparser.ConfigParser()
config.read("config.ini")

zip_code = config.get("settings", "zip_code")
manual_only = config.getboolean("settings", "manual_only")
radius = config.getint("settings", "radius")

def get_search_url(zip_code, radius=100):
    base_url = "https://www.vw.com/en/inventory.html/__app/inventory/results/golf-gti.app"
    url = f"{base_url}?distance-app={radius}&page-app=0&year-app=2023&zip-app={zip_code}"
    return url

def scrape_cars(url, manual_only):
    options = Options()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36")

    print("Starting the scraping process...") 

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Handle the cookies pop-up
    try:
        accept_cookies_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#ablehnTarget"))
        )
        accept_cookies_button.click()
    except TimeoutException:
        print("No cookies pop-up.")

    # Handle the feedback survey pop-up
    try:
        close_survey_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#uz_span_close"))
        )
        close_survey_button.click()
    except TimeoutException:
        print("No feedback survey pop-up.")

    # Handle the enter ZIP code pop-up
    try:
        submit_zipcode_button = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".sc-bXGyLb.bfGSd"))
        )
        submit_zipcode_button.click()
    except TimeoutException:
        print("No enter ZIP code pop-up.")

    # Apply the manual transmission filter
    if manual_only:
        ## open filters
        filter_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#Features"))  # Replace with the appropriate CSS selector
        )
        filter_element.click()
        time.sleep(2)

        ## select manual transmission option
        parent_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.StyledLabel-sc-tap8jg.btwHCA'))
        )

        manual_transmission_option = None
        for parent_element in parent_elements:
            child_element = parent_element.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
            if child_element.get_attribute('value') == "Manual":
                manual_transmission_option = parent_element
                break

        if manual_transmission_option:
            manual_transmission_option.click()
        else:
            print("Manual transmission option not found.")
        time.sleep(2)

        ## close filter
        # filter_element = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, "#Features"))
        # )
        # filter_element.click()
        time.sleep(5)  # Give some time for the page to fully load after applying the filter


    # Wait for the car elements to be present on the page
    wait = WebDriverWait(driver, 20)  # Change 10 to the maximum number of seconds you want to wait
    wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".result-card-wrapper")))

    soup = BeautifulSoup(driver.page_source, "html.parser")

    print("Scraping process completed.")

    # Find the car elements on the page
    cars = soup.select(".result-card-wrapper")

    for car in cars:
        car_trim = car.select_one(".result-card-car-trim").get_text(strip=True)  # Replace ".name-class-selector" with the appropriate CSS selector
        car_price = car.select_one(".result-card-price").get_text(strip=True)  # Replace ".price-class-selector" with the appropriate CSS selector

        dealer_tooltip = driver.find_element(By.CSS_SELECTOR, ".result-dealer-name")  
        ActionChains(driver).move_to_element(dealer_tooltip).perform()  # Hover over the dealer info for tooltip

        dealer_name = driver.find_element(By.CSS_SELECTOR, ".dealer-tooltip .styled-dealer-info .sc-jAaTju.jscYYl").text.strip()
        dealer_distance = driver.find_element(By.CSS_SELECTOR, '.dealer-tooltip .styled-dealer-info .sc-jAaTju.fjhxpY').text.strip()
        dealer_phone = driver.find_element(By.CSS_SELECTOR, '.dealer-tooltip .StyledTextComponent-sc-hqqa9q.hXYIcS').text.strip()

        print(f"\n Processing GTI: \n Trim: {car_trim}, \n Price: {car_price}, \n Dealer: {dealer_name}, \n Distance: {dealer_distance}, \n Phone: {dealer_phone}")
        
        
        # Process the car information, e.g., save to a file or send an email
        # ...

    driver.quit()

def main():
    url = get_search_url(zip_code, radius)
    scrape_cars(url, manual_only)

if __name__ == "__main__":
    main()

def job():
    url = get_search_url(zip_code)
    scrape_cars(url, manual_only)

# Schedule the job to run every hour (you can change this interval)
schedule.every(1).hours.do(job)

while True:
    schedule.run_pending()
    time.sleep(60)  # Wait for 60 seconds before checking again
