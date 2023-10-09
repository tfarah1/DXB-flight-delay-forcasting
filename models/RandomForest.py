import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor


class RandomForest():
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def run_model(self, n_estimators=10, random_state=0, max_depth=None, min_samples_split=2, min_samples_leaf=1, verbose=0):
        regressor = RandomForestRegressor(
            n_estimators=n_estimators, random_state=random_state,
            max_depth=max_depth, min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf, verbose=verbose)
        regressor.fit(self.X_train, self.y_train)
        return regressor

    def predict(self, regressor):
        y_pred = regressor.predict(self.X_test)
        return y_pred

    def show_predicted(self, y_pred):
        y_pred_array = np.array(y_pred)
        y_test_array = np.array(self.y_test)
        concatenated_array = np.concatenate(
            (y_pred_array.reshape(-1, 1), y_test_array.reshape(-1, 1)), axis=1)
        return concatenated_array

    def feature_importances(self, regressor):
        importances = regressor.feature_importances_
        feature_importance_df = pd.DataFrame(
            {'Feature': self.X_train.columns, 'Importance': importances})
        feature_importance_df = feature_importance_df.sort_values(
            by='Importance', ascending=False)
        return feature_importance_df

    @staticmethod
    def plot_feature_importances(feature_importance_df, figsize=(100, 60)):
        plt.figure(figsize=figsize)
        plt.barh(feature_importance_df['Feature'],
                 feature_importance_df['Importance'])
        plt.xlabel('Feature Importance')
        plt.ylabel('Feature')
        plt.title('Random Forest Feature Importances')
        plt.show()