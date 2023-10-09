import numpy as np
import json
import math
import holidays
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self, airport_json_data_path=None,
                 airport_lat=None, airport_lon=None, origin_df_col_name=None,
                 dest_df_col_name=None, new_distance_cols_names=None,
                 extracted_airline_col_name=None,
                 col_name_to_extract_airline_from=None,
                 relevant_years=None,
                 isHoliday_column_name=None,
                 col_to_extract_holiday_from=None,
                 date_col1_to_calc_delay=None,
                 date_col2_to_calc_delay=None,
                 date_format=None,
                 delay_col_name=None,
                 col_to_set_index=None,
                 index_col_name=None,
                 date_range=None,
                 ):

        self.airport_json_data_path = airport_json_data_path
        self.airport_lat = airport_lat
        self.airport_lon = airport_lon
        self.origin_df_col_name = origin_df_col_name
        self.dest_df_col_name = dest_df_col_name
        self.new_distance_cols_names = new_distance_cols_names
        self.extracted_airline_col_name = extracted_airline_col_name
        self.col_name_to_extract_airline_from = col_name_to_extract_airline_from
        self.relevant_years = relevant_years
        self.isHoliday_column_name = isHoliday_column_name
        self.col_to_extract_holiday_from = col_to_extract_holiday_from
        self.date_col1_to_calc_delay = date_col1_to_calc_delay
        self.date_col2_to_calc_delay = date_col2_to_calc_delay
        self.date_format = date_format
        self.delay_col_name = delay_col_name
        self.col_to_set_index = col_to_set_index
        self.index_col_name = index_col_name
        self.date_range = date_range

    def fit(self, X, y=None):
        return self

    # MAIN
    def transform(self, X):
        print('\nExtracting new features...')
        print('==========================')
        self.read_json_file()
        X_transformed = self.calc_origin_main_airport_destination_distances(X)
        X_transformed = self.extract_airline(X_transformed)
        X_transformed = self.check_holidays(X_transformed)
        # X_transformed.to_csv('res_features_extracted.csv')
        return X_transformed
    # / MAIN

    def read_json_file(self):
        with open(self.airport_json_data_path, "r") as json_file:
            data = json.load(json_file)
        self.airport_json_data = data

    @staticmethod
    def calc_haversine_distance(lat1, lon1, lat2, lon2):
        R = 6371
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * \
            math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def calc_origin_main_airport_destination_distances(self, dataframe):
        def calculate_total_distance(row):
            origin_coords = self.airport_json_data.get(
                row[self.origin_df_col_name], {})
            # dest_coords = self.airport_json_data.get(row[self.dest_df_col_name], {})
            if origin_coords:
                distance_origin_dubai = self.calc_haversine_distance(
                    origin_coords['lat'], origin_coords['lon'], self.airport_lat, self.airport_lon)
                # distance_dubai_dest = self.calc_haversine_distance(self.airport_lat, self.airport_lon,dest_coords['lat'], dest_coords['lon'])
                return distance_origin_dubai
            else:
                return np.nan
        dataframe[self.new_distance_cols_names[0]] = dataframe.apply(
            calculate_total_distance, axis=1, result_type='expand')
        return dataframe

    def extract_airline(self, dataframe):
        dataframe[self.extracted_airline_col_name] = dataframe[self.col_name_to_extract_airline_from].str[:2]
        dataframe.insert(1, self.extracted_airline_col_name,
                         dataframe.pop(self.extracted_airline_col_name))
        return dataframe

    def check_holidays(self, dataframe):
        dataframe[self.isHoliday_column_name] = 0
        uae_holidays = holidays.UnitedArabEmirates(years=self.relevant_years)
        for index, row in dataframe.iterrows():
            date = row[self.col_to_extract_holiday_from].date()
            if date in uae_holidays:
                dataframe.at[index, self.isHoliday_column_name] = 1
        return dataframe
