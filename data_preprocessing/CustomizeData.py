import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class CustomizeData(BaseEstimator, TransformerMixin):
    def __init__(self,
                 date_col1_to_calc_delay=None,
                 date_col2_to_calc_delay=None,
                 date_format=None,
                 delay_col_name=None,
                 col_to_set_index=None,
                 index_col_name=None,
                 date_range=None,
                 ):
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
        print('\nCustomizing Data...')
        print('===================')
        X_transformed = self.calc_delay(X)
        X_transformed = self.set_and_sort_index(X_transformed)
        X_transformed = self.filter_data_by_date_range(X_transformed)
        X_transformed.to_csv('customized_data_departure.csv')
        return X_transformed
    # / MAIN

    def calc_delay(self, dataframe):
        df = dataframe.copy()
        col1 = self.date_col1_to_calc_delay
        col2 = self.date_col2_to_calc_delay
        col1_SEC = col1+'_SEC'
        col2_SEC = col2+'_SEC'
        df[col1_SEC] = pd.to_datetime(df[col1], format=self.date_format)
        df[col2_SEC] = pd.to_datetime(df[col2], format=self.date_format)
        df[[col1_SEC, col2_SEC]] = df[[col1_SEC, col2_SEC]].apply(
            lambda x: x.dt.floor('T'))
        df[[col1_SEC, col2_SEC]] = df[[col1_SEC, col2_SEC]].apply(
            lambda x: (x.astype('int64') // 10**9).astype('int32'))
        df[self.delay_col_name] = (df[col2_SEC] - df[col1_SEC]) // 60
        return df

    def set_and_sort_index(self, dataframe):
        df = dataframe.copy()
        index_col_name = self.index_col_name
        df[index_col_name] = pd.to_datetime(
            df[self.col_to_set_index], format=self.date_format, errors='coerce')
        df[index_col_name] = df[index_col_name].dt.floor('T')
        df = df.sort_values(by=index_col_name)
        df.set_index(index_col_name, inplace=True)
        return df

    def filter_data_by_date_range(self, dataframe):
        filtered_df = dataframe[self.date_range[0]:self.date_range[1]]
        return filtered_df
