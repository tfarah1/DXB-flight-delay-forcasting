import csv
import json
from datetime import datetime


class WeatherDataOrganizer:
    def __init__(self, csv_file_path, output_JSON_PATH):
        self.csv_file_path = csv_file_path
        self.output_JSON_PATH = output_JSON_PATH
        self.organized_data = {}

    def process_csv(self):
        with open(self.csv_file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)

            for row in csv_reader:
                etoa = datetime.strptime(row['ETOA'], '%Y-%m-%d %H:%M:%S')

                temperature = row['ETOA_Temperature']
                dew_point = row['ETOA_Dew Point']
                humidity = row['ETOA_Humidity']
                wind = row['ETOA_Wind']
                wind_speed = row['ETOA_Wind Speed']
                wind_gust = row['ETOA_Wind Gust']
                pressure = row['ETOA_Pressure']
                precip = row['ETOA_Precip.']
                condition = row['ETOA_Condition']

                etoa_time = etoa.strftime('%I:%M %p')
                year = etoa.year
                month = etoa.strftime('%m')
                day = etoa.strftime('%d')
                hour = etoa.strftime('%H')

                if year not in self.organized_data:
                    self.organized_data[year] = {}

                if month not in self.organized_data[year]:
                    self.organized_data[year][month] = {}

                if day not in self.organized_data[year][month]:
                    self.organized_data[year][month][day] = {}

                if hour not in self.organized_data[year][month][day]:
                    self.organized_data[year][month][day][hour] = {
                        "Time": etoa_time,
                        "Temperature": temperature,
                        "Dew Point": dew_point,
                        "Humidity": humidity,
                        "Wind": wind,
                        "Wind Speed": wind_speed,
                        "Wind Gust": wind_gust,
                        "Pressure": pressure,
                        "Precip.": precip,
                        "Condition": condition
                    }

    def sort_data(self):
        for year in self.organized_data:
            for month in self.organized_data[year]:
                for day in self.organized_data[year][month]:
                    self.organized_data[year][month][day] = dict(
                        sorted(self.organized_data[year][month][day].items()))
                self.organized_data[year][month] = dict(
                    sorted(self.organized_data[year][month].items()))

        for year in self.organized_data:
            self.organized_data[year] = dict(
                sorted(self.organized_data[year].items()))

    def save_to_json(self):
        with open(self.output_JSON_PATH, 'w') as json_file:
            json.dump(self.organized_data, json_file, indent=4)


if __name__ == "__main__":
    csv_file_path = "C:/Users/Admin/Desktop/jsoncsv.csv"
    output_JSON_PATH = "C:/Users/Admin/Desktop/weather scraping/assets/JSON_Files/complete/weather.json"

    weather_organizer = WeatherDataOrganizer(csv_file_path, output_JSON_PATH)
    weather_organizer.process_csv()
    weather_organizer.sort_data()
    weather_organizer.save_to_json()

    print("Data has been saved to 'weather_org.json'")
