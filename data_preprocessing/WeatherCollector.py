import json
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class WeatherCollector(BaseEstimator, TransformerMixin):
    def __init__(self, weather_JSON_PATH, datetime_column, initial_columns, new_column_names):
        self.weather_JSON_PATH = weather_JSON_PATH
        self.datetime_column = datetime_column
        self.initial_columns = initial_columns
        self.new_column_names = new_column_names
        self.weather_data = None

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print('\nCollecting Weather Data...')
        print('==========================')
        self.load_json_data()
        X_transformed = self.merge_weather_data(X)
        X_transformed = self.fix_column_names(X_transformed)
        return X_transformed

    def load_json_data(self):
        with open(self.weather_JSON_PATH, 'r') as json_file:
            data = json.load(json_file)
            self.weather_data = data

    def merge_weather_data(self, dataframe):
        merged_data = dataframe.to_numpy()
        updated_merged_data = []
        etoa_index = dataframe.columns.get_loc(self.datetime_column)
        for row in merged_data:
            etoa_datetime = datetime.strptime(row[etoa_index], '%Y%m%d%H%M%S')
            year = str(etoa_datetime.year)
            month = str(etoa_datetime.month).zfill(2)
            day = str(etoa_datetime.day).zfill(2)
            hour = str(etoa_datetime.hour).zfill(2)

            if year in self.weather_data and month in self.weather_data[year] \
                    and day in self.weather_data[year][month] \
                    and hour in self.weather_data[year][month][day]:
                weather_info = self.weather_data[year][month][day][hour]
                new_values_list = list(weather_info.values())
                row_list = row.tolist()
                row_list.extend(new_values_list)
                updated_row = np.array(row_list)
                updated_merged_data.append(updated_row)
            else:
                updated_merged_data.append(row)
        return pd.DataFrame(updated_merged_data)

    def fix_column_names(self, dataframe):
        column_names = list(self.initial_columns) + self.new_column_names
        dataframe.columns = column_names
        return dataframe
