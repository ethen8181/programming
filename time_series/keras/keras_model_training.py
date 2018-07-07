def main():
    import os
    import time
    import logging
    import pandas as pd
    from logzero import setup_logger
    from timeseries.generators import time_series_generator
    from timeseries.keras_utils import KerasPipeline

    # -----------------------------------------------------------------------------------
    # Adjustable Parameters
    input_path = 'jena_climate_2009_2016.csv'
    train_size = 200000
    model_checkpoint = 'model_checkpoint'

    # prepend a timestamp, e.g. 20180324_113330 for the current model directory;
    # the current model directory will store the model checkpoint and log file
    model_dir = 'model'
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    current_model_dir = 'keras_{}'.format(timestamp)

    # -----------------------------------------------------------------------------------
    start = time.time()
    current_model_path = os.path.join(model_dir, current_model_dir)
    if not os.path.isdir(current_model_path):
        os.makedirs(current_model_path, exist_ok=True)

    logfile = os.path.join(current_model_path, 'modeling.log')
    logger = setup_logger(name=__name__, logfile=logfile, level=logging.INFO)

    logger.info('preprocessing')
    df = pd.read_csv(input_path)  # TODO remove reading whole dataset in
    label_col = 'T (degC)'
    label_index = df.columns.tolist().index(label_col)

    logger.info('preprocessed data shape: {} rows, {} columns'.format(*df.shape))
    logger.info('sample preprocessed data:\n{}'.format(df.head()))

    # TODO change the hard-coded 1:
    X = df[df.columns[1:]].values
    mean = X[:train_size].mean(axis=0)
    X -= mean
    std = X[:train_size].std(axis=0)
    X /= std

    lookback = 1440
    step = 6
    delay = 144
    batch_size = 128
    train_gen = time_series_generator(
        X,
        label_index=label_index,
        lookback=lookback,
        delay=delay,
        min_index=0,
        max_index=200000,
        shuffle=True,
        step=step,
        batch_size=batch_size)
    val_gen = time_series_generator(
        X,
        label_index=label_index,
        lookback=lookback,
        delay=delay,
        min_index=200001,
        max_index=300000,
        step=step,
        batch_size=batch_size)
    test_gen = time_series_generator(
        X,
        label_index=label_index,
        lookback=lookback,
        delay=delay,
        min_index=300001,
        max_index=None,
        step=step,
        batch_size=batch_size)

    input_shape = None, X.shape[1]
    val_steps = (300000 - 200001 - lookback) // batch_size
    model = KerasPipeline(input_shape)
    model.fit_generator(
        train_gen, steps_per_epoch=500, epochs=1,
        validation_data=val_gen, validation_steps=val_steps)
    model.save(os.path.join(current_model_path, model_checkpoint))

    end = time.time()
    elapse = (end - start) / 60
    logger.info('Took {} minutes to run the end to end pipeline'.format(elapse))


if __name__ == '__main__':
    main()
