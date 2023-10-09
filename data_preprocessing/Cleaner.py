import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class Cleaner(BaseEstimator, TransformerMixin):
    def __init__(self, columns_to_drop=None,
                 illogical_order_cols=None,
                 columns_to_check=None,
                 values_to_drop=None):

        self.columns_to_drop = columns_to_drop
        self.illogical_order_cols = illogical_order_cols
        self.columns_to_check = columns_to_check
        self.values_to_drop = values_to_drop

    def fit(self, X, y=None):
        return self

    # MAIN
    def transform(self, X):
        print('Cleaning Data...')
        print('================')
        X_transformed = self.drop_rows_with_missing_or_whitespace(X)
        X_transformed = self.drop_columns(X_transformed)
        X_transformed = self.drop_rows_by_values(X_transformed)
        X_transformed = self.drop_illogical_time_sequence_rows(X_transformed)
        # X_transformed = self.generate_sequential_ids(X_transformed)
        return X_transformed
    # / MAIN

    def drop_rows_with_missing_or_whitespace(self, dataframe):
        bef = len(dataframe)
        dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
        dataframe = dataframe.dropna()
        af = len(dataframe)
        print(f"Dropped: {bef - af} rows.\n")
        return dataframe

    def drop_columns(self, dataframe):
        return dataframe.drop(columns=self.columns_to_drop, errors='ignore')

    def drop_illogical_time_sequence_rows(self, dataframe):
        for column_pair_with_formats in self.illogical_order_cols:
            timestamp_format = column_pair_with_formats[0]
            column_pairs = column_pair_with_formats[1:]
            for pair in column_pairs:
                before_col = pair[0]
                after_col = pair[1]
                dataframe.loc[:, before_col] = pd.to_datetime(
                    dataframe[before_col], format=timestamp_format)
                dataframe.loc[:, after_col] = pd.to_datetime(
                    dataframe[after_col], format=timestamp_format)

            rows_to_keep = dataframe.apply(lambda row: all(
                row[before_col] < row[after_col] for before_col, after_col in column_pairs), axis=1)
            dataframe = dataframe[rows_to_keep]
        return dataframe

    def drop_rows_by_values(self, dataframe):
        return dataframe[~dataframe[self.columns_to_check].isin(self.values_to_drop).any(axis=1)]

    def generate_sequential_ids(self, dataframe):
        dataframe.insert(0, 'ID', range(1, len(dataframe) + 1))
        return dataframe
