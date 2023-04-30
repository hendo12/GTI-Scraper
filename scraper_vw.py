import requests
from bs4 import BeautifulSoup
import json
import time
import schedule
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    options.add_argument('--headless')
    
    print("Starting the scraping process...") 
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Give some time for the page to fully load

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    print("Scraping process completed.")
    
    # Find the car elements on the page
    cars = soup.select(".car-class-selector")  # Replace ".car-class-selector" with the appropriate CSS selector

    for car in cars:
        car_name = car.select_one(".name-class-selector").get_text(strip=True)  # Replace ".name-class-selector" with the appropriate CSS selector
        car_price = car.select_one(".price-class-selector").get_text(strip=True)  # Replace ".price-class-selector" with the appropriate CSS selector
        car_location = car.select_one(".location-class-selector").get_text(strip=True)  # Replace ".location-class-selector" with the appropriate CSS selector
        car_transmission = car.select_one(".transmission-class-selector").get_text(strip=True)  # Replace ".transmission-class-selector" with the appropriate CSS selector

        print(f"Processing car: {car_name}, {car_price}, {car_location}, {car_transmission}")
        
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
