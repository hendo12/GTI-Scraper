# Volkswagen GTI Inventory Scraper

This Python script scrapes the Volkswagen GTI inventory from the official VW website and filters the results based on specified criteria (e.g., manual transmission). The script can be scheduled to run periodically to monitor the inventory for new listings.

## Prerequisites

Before running the script, ensure you have the following installed:

1. Python 3.6 or later
2. Google Chrome browser
3. ChromeDriver (compatible with your Chrome version)

Additionally, you need to run the following command in the terminal to install the required Python packages:

```python
pip install -r requirements.txt
```

## Configuration

The `config.ini` file contains the following settings that you can update as needed:

- `zip_code`: The zip code for searching the inventory
- `manual_only`: Set to `True` if you want to search for manual transmission cars only, otherwise set to `False`
- `radius`: The search radius (in miles) around the specified zip code

## Running the script

To run the script, execute the following command:

```python
python scraper.py
```

By default, the script will run once when executed. You can modify the scheduling interval in the `scraper_vw.py` file by updating the following line:

```python
schedule.every(1).hours.do(job)
```

Change the 1 to the desired interval (in hours) between scraper runs.

## Output

The script will print the progress and the car information as it scrapes the inventory. You can update the scrape_cars() function to process the car information as needed (e.g., save to a file, send an email).

## Todo

- What to do with the output
- automate an email or text to dealer if criteria are met
- alert me when this has happened
- fix total price output
- refactor code

## License

This project is licensed under the MIT License. See the LICENSE file for details.
