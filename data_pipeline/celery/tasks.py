from pandas_datareader import DataReader
from celeryapp import app


@app.task
def get_stock_info(stock, start, end, source = 'yahoo'):
    stock_col = 'Stock'
    df = DataReader(stock, source, start, end)
    df[stock_col] = stock
    agg = df.groupby(stock_col).agg(['min', 'max', 'mean', 'median'])
    agg.columns = [' '.join(col) for col in agg.columns.values]
    return agg.to_json()
