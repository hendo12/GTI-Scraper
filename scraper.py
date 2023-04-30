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

config = configparser.ConfigParser()
config.read("config.ini")

zip_code = config.get("settings", "zip_code")
manual_only = config.getboolean("settings", "manual_only")
radius = config.getint("settings", "radius")

def get_search_url(zip_code, radius=100):
    base_url = "https://www.vw.com/en/inventory.html/__app/inventory/results/golf-gti.app"
    url = f"{base_url}?distance-app={radius}&page-app=0&year-app=2023&zip-app={zip_code}"
    return url

def scrape_cars(url, manual_only=True):
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


    # Wait for the car elements to be present on the page
    wait = WebDriverWait(driver, 20)  # Change 10 to the maximum number of seconds you want to wait
    wait.until(EC.visibility_of_any_elements_located((By.CSS_SELECTOR, ".result-card-wrapper")))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    print("Scraping process completed.")

    # Find the car elements on the page
    cars = soup.select(".result-card-wrapper")

    print("Cars: ", cars)

    for car in cars:
        car_name = car.select_one(".result-card-car-trim").get_text(strip=True)  # Replace ".name-class-selector" with the appropriate CSS selector
        car_price = car.select_one(".result-card-price").get_text(strip=True)  # Replace ".price-class-selector" with the appropriate CSS selector
        car_location = car.select_one(".result-dealer-name").get_text(strip=True)  # Replace ".location-class-selector" with the appropriate CSS selector
        car_distance = car.select_one('.result-dealer-distance')
        car_transmission = car.select_one(".transmission-class-selector").get_text(strip=True)  # Replace ".transmission-class-selector" with the appropriate CSS selector

        print(f"Processing car: {car_name}, {car_price}, {car_location}, {car_distance}, {car_transmission}")
        
        if manual_only and "manual" not in car_transmission.lower():
            continue
        
        # Process the car information, e.g., save to a file or send an email
        # ...

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
