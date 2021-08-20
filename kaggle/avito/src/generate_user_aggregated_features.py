"""
Generate user aggregated statistics/features from the periods and active .csv file and
save it under the 'data' folder along with the raw data. This script can be run once and
the file can be used for all future runs. Right now this script generates a single parquet
file which includes records from both train and test, it could be further optimized to
separate them out, so we only need to read in records related to training when performing
the pre-processing step for the training data and the same applies to the test data.

The script takes approx. 5 minutes

References
----------
https://www.kaggle.com/bminixhofer/aggregated-features-lightgbm?scriptVersionId=3645705/code
"""
import os
import pandas as pd
from time import time
from logzero import setup_logger
logger = setup_logger()


def main():
    # -----------------------------------------------------------------------------------
    # Adjustable Parameters
    # the output will be saved as a parquet file as oppose to a
    # csv file for faster reading in the future
    output_file = 'aggregated_user_features.parquet'
    input_dir = os.path.join('..', 'data')
    ids_col = 'item_id'
    user_col = 'user_id'

    # generated aggregated statistics' column names
    days_up_sum_col = 'days_up_sum'
    times_put_up_col = 'times_put_up'

    # -----------------------------------------------------------------------------------
    logger.info('generating item aggregated statistics')
    start = time()

    df_item_agg_stats = generate_item_agg_stats(input_dir, ids_col, days_up_sum_col, times_put_up_col)
    df_active = concat_active_data(input_dir, ids_col, user_col)
    df_item_agg_stats = df_item_agg_stats.merge(df_active, on=ids_col, how='inner')
    logger.info('item aggregated statistics data shape: {}'.format(df_item_agg_stats.shape))
    logger.info('sample item aggregated statistics data:\n{}'.format(df_item_agg_stats.head()))

    logger.info('generating user aggregated statistics')
    df_user_agg_stats = generate_user_agg_stats(
        df_item_agg_stats, user_col, ids_col, days_up_sum_col, times_put_up_col)
    logger.info('user aggregated statistics data shape: {}'.format(df_user_agg_stats.shape))
    logger.info('sample user aggregated statistics data:\n{}'.format(df_user_agg_stats.head()))

    logger.info('saving user aggregated statistics as a parquet file')
    output_path = os.path.join(input_dir, output_file)
    df_user_agg_stats.to_parquet(output_path)

    end = time()
    elapse = (end - start) / 60
    logger.info('Took {} minutes to generate user-level aggregate statistics'.format(elapse))


def generate_user_agg_stats(df_item_agg_stats, user_col, ids_col, days_up_sum_col, times_put_up_col):
    """
    Given the aggregated stats for each item id, which also has its corresponding user id (indicating
    the user that listed the item), we now aggregate the stats based on user.

    For each user, we would have the average/std number of days he/she likes to list his/her items and the
    average/std number of times he/she likes to list his/her items and the number of items that he/she
    has listed.

    e.g.
         user_id  days_up_sum_mean  days_up_sum_std  times_put_up_mean  times_put_up_std  user_item_count
    00000077ff21              12.5         3.535534               2.00          0.000000                2
    000006497719              19.0      -999.000000               2.00       -999.000000                1
    00000b4d72f6               3.0      -999.000000               1.00       -999.000000                1
    00000d642d7e              13.0         0.000000               1.00          0.000000                2
    0000126b80a4              12.0         5.606119               1.75          1.035098                8
    """
    grouped = df_item_agg_stats.groupby(user_col)[[days_up_sum_col, times_put_up_col]]
    df_grouped = grouped.aggregate(['mean', 'std'])

    # renaming multi-level index column names (generated when performing groupby)
    # https://stackoverflow.com/questions/19078325/naming-returned-columns-in-pandas-aggregate-function
    df_grouped.columns = ['_'.join(x) for x in df_grouped.columns.ravel()]

    # not all users have listed multiple item ids, hence their standard
    # deviation will be null, impute them with a na flag
    na_flag = -999
    std_cols = [col for col in df_grouped.columns if col.endswith('std')]
    df_grouped[std_cols] = df_grouped[std_cols].fillna(na_flag)

    n_user_items = df_item_agg_stats.groupby(user_col)[[ids_col]].count()
    n_user_items.columns = ['user_item_count']

    df_user_agg_stats = df_grouped.merge(n_user_items, on=user_col, how='inner')
    return df_user_agg_stats.reset_index()


def generate_item_agg_stats(input_dir, ids_col, days_up_sum_col, times_put_up_col):
    """
    Generate aggregated stats for each item id.
    For each item id, we will generate two additional aggregated statistics:
    1. total number of days that the item id is up.
    2. number of times that the item id is listed.

    e.g.
            item_id  days_up_sum  times_put_up       user_id
    0  00000077ff21           13             1  3c0ae6a131ee
    1  000002c54018            6             1  ce6e0b01561c
    2  000005570503            1             1  1bfc41de9f99
    3  0000060018e6            6             1  cf4f54affdaf
    4  000006497719           19             2  b3953ce33d94
    """
    days_up_col = 'days_up'
    date_to_col = 'date_to'
    date_from_col = 'date_from'
    df_periods = concat_periods_data(input_dir, ids_col, date_to_col, date_from_col)
    df_periods[days_up_col] = df_periods[date_to_col].dt.dayofyear - df_periods[date_from_col].dt.dayofyear

    # generate agg stats
    grouped = df_periods.groupby(ids_col)[[days_up_col]]
    df_grouped = grouped.aggregate(['sum', 'count'])
    df_grouped.columns = df_grouped.columns.droplevel(0)
    df_agg_stats = (df_grouped.
                    reset_index().
                    rename(columns={'sum': days_up_sum_col, 'count': times_put_up_col}))
    return df_agg_stats


def concat_periods_data(input_dir, ids_col, date_to_col, date_from_col):
    use_cols = [ids_col, date_to_col, date_from_col]
    parse_dates = [date_to_col, date_from_col]
    path_train_periods = os.path.join(input_dir, 'periods_train.csv')
    path_test_periods = os.path.join(input_dir, 'periods_test.csv')

    df_train_periods = pd.read_csv(path_train_periods, usecols=use_cols, parse_dates=parse_dates)
    df_test_periods = pd.read_csv(path_test_periods, usecols=use_cols, parse_dates=parse_dates)
    df_periods = pd.concat([df_train_periods, df_test_periods])
    return df_periods


def concat_active_data(input_dir, ids_col, user_col):
    """
    There are multiple rows with the same item_id in the train_active and test_active data.
    This is expected as an item_id can be listed multiple times, though we will need
    to drop the duplicates when calculating aggregated statistics.
    """
    use_cols = [ids_col, user_col]
    path_train_active = os.path.join(input_dir, 'train_active.csv')
    path_test_active = os.path.join(input_dir, 'test_active.csv')

    df_train_active = pd.read_csv(path_train_active, usecols=use_cols)
    df_test_active = pd.read_csv(path_test_active, usecols=use_cols)
    df_active = pd.concat([df_train_active, df_test_active]).drop_duplicates(ids_col)
    return df_active


if __name__ == '__main__':
    main()
