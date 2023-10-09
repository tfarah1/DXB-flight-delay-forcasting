import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from feature_engine.creation import CyclicalFeatures
from feature_engine.datetime import DatetimeFeatures


def count_columns_start_with(df, keyword):
    print(
        f"{len([x for x in df.columns.tolist() if x.startswith(keyword)])} columns start with {keyword}")


def show_columns(df):
    for i in df.columns.tolist():
        print(f"'{i}'", end=',')


def load_data(filename, columns, index_column, frequency):
    data = pd.read_csv(
        filename,
        usecols=columns,
        parse_dates=[index_column],
        index_col=[index_column])
    data = data[~data.index.duplicated(keep='first')]
    data = data.resample(frequency)
    data = data.fillna(method="ffill")
    return data


def calc_mean_and_sort(df, group_column, aggregate_column):
    mean_df = df.groupby(group_column)[aggregate_column].mean().reset_index()
    mean_df = mean_df.sort_values(by=aggregate_column, ascending=False)
    return mean_df


def plot_mean_delay_per_grp(df, x_column, y_column, x_label, y_label,
                            title, rotation=0, ha='center',
                            figsize=(10, 6), color='blue'):
    # x_column: Flight_Type, y_column: delay
    plt.figure(figsize=figsize)
    plt.bar(df[x_column], df[y_column], color=color)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(rotation=rotation, ha=ha)
    plt.tight_layout()
    plt.show()


def plot_mean_delay(df, group_name, numeric_column, color, figsize=(8, 4)):
    mean_df = calc_mean_and_sort(df, group_name, numeric_column)
    plot_mean_delay_per_grp(mean_df, group_name, numeric_column,
                            group_name, 'Mean ' +
                            numeric_column, 'Mean ' + numeric_column
                            + ' per ' + group_name, color=color, figsize=figsize)


def plot_delay_with_outliers(data, y_column, title, ylabel, xlabel, marker='.', figsize=(10, 5), legend=True, color='purple'):
    fig, ax = plt.subplots(figsize=figsize)
    data.plot(y=y_column, marker=marker, figsize=figsize,
              legend=legend, ax=ax, color=color)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    plt.show()


def evaluate_model(y_test, y_pred):
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    print('R2:', r2, '\nMSE:', mse, '\nMAE:',
          mae, '\nMAPE:', mape, '\nRMSE:', rmse)


def show_error(y_test, y_pred):
    y_test_flattened = np.ravel(y_test)
    y_pred_flattened = np.ravel(y_pred)
    y_pred_flattened = np.round(y_pred_flattened)
    df = pd.DataFrame({
        'Actual': y_test_flattened,
        'Predicted': y_pred_flattened
    })
    df['Error'] = np.abs(df['Actual'] - df['Predicted'])
    return df


def transform_datetime(df, col_name):
    df_copy = df.copy()
    dtf = DatetimeFeatures(
        variables=col_name,
        features_to_extract=[
            "month",
            "hour",
            "weekend",
        ],
    )
    cyclicf = CyclicalFeatures(
        variables=[col_name + "_month", col_name + "_hour"],
        drop_original=False)

    df_copy = dtf.fit_transform(df_copy)
    df_copy = cyclicf.fit_transform(df_copy)
    return df_copy
