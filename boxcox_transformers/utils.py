import pandas as pd


def clean(filepath, now, cat_cols, str_cols, num_cols, date_cols, ids_col, label_col = None):
    """
    Clean the raw dataset, targeted for this specific problem. Details
    of the preprocessing steps are commented within the function

    Parameters
    ----------
    filepath : str
        Relative filepath of the data

    now : str
        Date in the format of YYYY-MM-DD to compute the
        recency feature

    cat_cols : list[str]
        Categorical features' column names

    str_cols : list[str]
        String features' column names, str_cols are essentially
        categorical columns but includes NA values, thus they are
        read in as is and converted to categorical type after
        imputing the unknowns

    num_cols : list[str]
        Numeric features' column names

    date_cols : list[str]
        Datetime features' column names

    ids_col : str
        ID column name

    label_col : str, default None
        Label column's name, None indicates that we're dealing with
        new data that does not have the label column

    Returns
    -------
    data : DataFrame
        Cleaned data
    """

    # information used when reading in the .csv file
    cat_dtypes = {col: 'category' for col in cat_cols}
    read_csv_info = {'dtype': cat_dtypes,
                     'parse_dates': date_cols,
                     'infer_datetime_format': True}
    use_cols = cat_cols + num_cols + date_cols + [ids_col]
    if label_col is not None:
        use_cols += [label_col]

    data = pd.read_csv(filepath, usecols = use_cols, **read_csv_info)

    # OWN_RENT has 5 distinct types, but there's only 2 records
    # for type "C", 1 record for both type "A", "B", these records
    # are simply dropped. Type "O" and "R" is kept
    data = data[~data['OWN_RENT'].isin(['C', 'A', 'B'])]

    # null values per row
    data['NAN_COUNT'] = data.isnull().sum(axis = 1)

    # NAN is filled with "unknown", after that we can
    # safely convert them to categorical tye
    data[str_cols] = data[str_cols].fillna('unknown')
    for str_col in str_cols:
        data[str_col] = data[str_col].astype('category')

    # there's only 1 date column in the date_cols list,
    # use it to compute the recency
    date_col = date_cols[0]
    data[date_col] = (pd.Timestamp(now) - data[date_col]).dt.days
    return data
