import json
import time
import signal
import datetime
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService


class WeatherScraper():
    def __init__(self, chrome_driver_PATH, result_JSON_PATH, required_weather_columns, country_city,
                 start_year=2016, end_year=2016, start_month=1, end_month=1):
        self.chrome_driver_PATH = chrome_driver_PATH
        self.result_JSON_PATH = result_JSON_PATH
        self.required_weather_columns = required_weather_columns
        self.country_city = country_city
        self.weather_data_dict = {}
        self.last_scraped_date = None
        self.start_year = start_year
        self.end_year = end_year
        self.start_month = start_month
        self.end_month = end_month

    def get_weather_data(self, date, country_city):
        url = f"https://www.wunderground.com/history/daily/{country_city}/date/{date}"

        service = ChromeService(executable_path=self.chrome_driver_PATH)
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(5)
        try:
            tables = driver.find_elements(By.TAG_NAME, 'table')
            for table in tables:
                header_row = table.find_element(
                    By.TAG_NAME, 'thead').find_element(By.TAG_NAME, 'tr')
                header_columns = header_row.find_elements(By.TAG_NAME, 'th')
                header_texts = [column.text for column in header_columns]
                if all(column in header_texts for column in self.required_weather_columns):
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    weather_data = []
                    for row in rows[1:]:
                        columns = row.find_elements(By.TAG_NAME, 'td')
                        data = [column.text for column in columns]
                        if len(data) >= len(self.required_weather_columns):
                            weather_data.append(data)
                    driver.quit()
                    return weather_data
            driver.quit()
            return None
        except Exception as e:
            print(f"Error while scraping: {e}")
            driver.quit()
            return None

    def load_weather_data(self):
        try:
            with open(self.result_JSON_PATH, 'r') as json_file:
                data = json.load(json_file)
                self.weather_data_dict = data.get('data', {})
                self.last_scraped_date = data.get('last_scraped_date')
                print('Last Scraped Date: ', self.last_scraped_date)
        except FileNotFoundError:
            print("No previous data found. Starting from scratch.")

    def save_weather_data(self):
        organized_data = {}
        for date, weather_data in self.weather_data_dict.items():
            year, month, day = date.split('-')
            if year not in organized_data:
                organized_data[year] = {}
            if month not in organized_data[year]:
                organized_data[year][month] = {}
            if day not in organized_data[year][month]:
                organized_data[year][month][day] = {}
            for entry in weather_data:
                entry_time = entry[0]
                hour = datetime.strptime(entry_time, '%I:%M %p').strftime('%H')
                if hour not in organized_data[year][month][day]:
                    organized_data[year][month][day][hour] = {
                        self.required_weather_columns[0]: entry[0],
                        self.required_weather_columns[1]: entry[1].split(' ')[0],
                        self.required_weather_columns[2]: entry[2].split(' ')[0],
                        self.required_weather_columns[3]: entry[3].split(' ')[0],
                        self.required_weather_columns[4]: entry[4],
                        self.required_weather_columns[5]: entry[5].split(' ')[0],
                        self.required_weather_columns[6]: entry[6].split(' ')[0],
                        self.required_weather_columns[7]: entry[7].split(' ')[0],
                        self.required_weather_columns[8]: entry[8].split(' ')[0],
                        self.required_weather_columns[9]: entry[9]
                    }
        with open(self.result_JSON_PATH, 'w') as json_file:
            data = {
                'data': organized_data,
                'last_scraped_date': self.last_scraped_date
            }
            json.dump(data, json_file, indent=4)

    def find_closest_hour(self, date, weather_data):
        target_hour = date.hour
        closest_hour = min(weather_data, key=lambda x: abs(
            datetime.strptime(x[0], '%I:%M %p').hour - target_hour))
        print(f"Date: {date.strftime('%I-%p')}, Closest Hour: {closest_hour}")
        return closest_hour

    def scrape_weather_data(self, start_year, end_year, start_month=1, end_month=1):
        year_range = range(start_year, end_year + 1)
        if start_month is None or end_month is None:
            month_range = range(1, 13)
        else:
            month_range = range(start_month, end_month + 1)
        for year in year_range:
            for month in month_range:
                days_in_month = 31
                if month in [4, 6, 9, 11]:
                    days_in_month = 30
                elif month == 2:
                    days_in_month = 29 if year % 4 == 0 and (
                        year % 100 != 0 or year % 400 == 0) else 28
                start_day = 1
                if self.last_scraped_date:
                    last_date = datetime.strptime(
                        self.last_scraped_date, "%Y-%m-%d")
                    if last_date.year == year and last_date.month == month:
                        start_day = last_date.day + 1
                for day in range(start_day, days_in_month + 1):
                    date_str = f"{year:04d}-{month:02d}-{day:02d}"
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    print(f'\n\nDate Object: {date_obj}\n\n')
                    weather_data = self.get_weather_data(
                        date_obj, self.country_city)
                    if weather_data is not None:
                        self.weather_data_dict[date_str] = weather_data
                        print(f"Collected data for {date_str}: {weather_data}")
                    self.last_scraped_date = date_str
                    time.sleep(2)
        self.save_weather_data(self.result_JSON_PATH)

    def run(self):
        self.load_weather_data()

        def signal_handler(signal, frame):
            print("Interrupt received. Saving data to JSON...")
            self.save_weather_data()
            print("Data saved. Exiting.")
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        if self.last_scraped_date:
            last_date = datetime.strptime(self.last_scraped_date, "%Y-%m-%d")
            start_year = last_date.year
            end_year = last_date.year
            new_data = self.scrape_weather_data(start_year, end_year)
        else:
            new_data = self.scrape_weather_data(
                self.start_year, self.end_year, self.start_month, self.end_month)

        if new_data:
            latest_date = max(new_data.keys())
            self.last_scraped_date = latest_date
            self.save_weather_data(self.result_JSON_PATH)


if __name__ == "__main__":
    result_JSON_PATH = 'C:/Users/Admin/Desktop/weather scraping/assets/JSON_Files/scraped_weather.json'
    chrome_driver_PATH = "C:/Program Files (x86)/chromedriver.exe"
    required_weather_columns = ['Time', 'Temperature', 'Dew Point', 'Humidity',
                                'Wind', 'Wind Speed', 'Wind Gust', 'Pressure', 'Precip.', 'Condition']
    country_city = 'ae/dubai'

    start_year = 2023
    end_year = 2023
    start_month = 3
    end_month = 3

    scraper = WeatherScraper(chrome_driver_PATH=chrome_driver_PATH,
                             result_JSON_PATH=result_JSON_PATH,
                             required_weather_columns=required_weather_columns,
                             country_city=country_city,
                             start_year=start_year,
                             end_year=end_year,
                             start_month=start_month,
                             end_month=end_month)

    scraper.run()