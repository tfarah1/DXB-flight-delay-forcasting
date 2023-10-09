import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class FeaturePreProcessing(BaseEstimator, TransformerMixin):
    def __init__(self,
                 encoding_method,
                 categories,
                 delay_column=None,
                 pareto_percentage=None):

        self.encoding_method = encoding_method
        self.categories = categories
        self.delay_column = delay_column
        self.pareto_percentage = pareto_percentage
        self.mean_delay_per_group_df = pd.DataFrame()

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        print('\nPreProcessing Data...')
        print('=====================')
        X_transformed = self.encode_data(X)
        return X_transformed

    @staticmethod
    def calc_mean_delay_per_group(dataframe, category, delay_column):
        return dataframe.groupby(category)[delay_column].mean()

    def encode_mean_delay(self, dataframe):
        for category in self.categories:
            new_col_name = category + '_Mean_' + self.delay_column
            mean_delay_per_group_df = self.calc_mean_delay_per_group(
                dataframe, category, self.delay_column)
            dataframe[new_col_name] = dataframe[category].map(
                mean_delay_per_group_df)
        # dataframe.drop(columns=[self.categories], inplace=True)
        return dataframe

    def onehot_encode(self, dataframe, columns=None):
        if columns:
            cols = columns
        else:
            cols = self.categories
        encoded_df = pd.get_dummies(dataframe, columns=cols, dtype=int)
        return encoded_df

    def encode_top_categories(self, dataframe):
        encoded_df = dataframe.copy()
        for category in self.categories:
            category_counts = dataframe[category].value_counts()
            top_categories = category_counts.head(
                int(len(category_counts) * self.pareto_percentage)).index
            # print(category, ': ', len(top_categories), 'categories.')
            encoded_df[category + '_encoded'] = dataframe[category].apply(
                lambda x: x if x in top_categories else 'Other')
        cats = [category + '_encoded' for category in self.categories]
        onehot_encoded_df = self.onehot_encode(encoded_df, columns=cats)
        return onehot_encoded_df

    def encode_data(self, dataframe):
        encoded_df = pd.DataFrame()
        if self.encoding_method == "pareto_encoding":
            encoded_df = self.encode_top_categories(dataframe)
        elif self.encoding_method == "mean_encoding":
            encoded_df = self.encode_mean_delay(dataframe)
        elif self.encoding_method == "onehot_encoding":
            encoded_df = self.onehot_encode(dataframe)
        return encoded_df
