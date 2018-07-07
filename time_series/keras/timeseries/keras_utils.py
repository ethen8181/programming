import os
from keras.models import Sequential
from keras.layers import GRU, Dense
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping


class KerasPipeline:

    def __init__(self, input_shape=None):
        self.input_shape = input_shape
        self._model_checkpoint = 'model.h5'
        self._history_checkpoint = 'history.pkl'
        self._figure_checkpoint = 'loss_history.png'

    def fit_generator(self, generator, steps_per_epoch=None, epochs=1, verbose=1,
                      callbacks=None, validation_data=None, validation_steps=None,
                      class_weight=None, max_queue_size=10, workers=1,
                      use_multiprocessing=False, shuffle=True, initial_epoch=0):
        """
        """
        if callbacks is None:
            # TODO include tensorboard and cyclical learning rate
            stop = EarlyStopping(monitor='val_loss', min_delta=0,
                                 patience=5, verbose=1, mode='auto')
            callbacks = [stop]

        model = self._create_model()
        history = model.fit_generator(
            generator=generator, steps_per_epoch=steps_per_epoch, epochs=epochs,
            verbose=verbose, callbacks=callbacks, validation_data=validation_data,
            validation_steps=validation_steps, class_weight=class_weight,
            max_queue_size=max_queue_size, workers=workers,
            use_multiprocessing=use_multiprocessing, shuffle=shuffle, initial_epoch=initial_epoch)

        self.model_ = model
        self.history_ = history.history
        return self

    def _create_model(self):
        metrics = None
        model = Sequential()
        model.add(GRU(16, input_shape=self.input_shape))
        model.add(Dense(1))
        model.compile(optimizer=RMSprop(), loss='mse', metrics=metrics)
        return model

    def save(self, path):
        from joblib import dump

        if not os.path.isdir(path):
            os.mkdir(path)

        model_checkpoint, history_checkpoint, figure_checkpoint = self._get_checkpoint_path(path)
        self.model_.save(model_checkpoint)
        dump(self.history_, history_checkpoint)
        self.visualize_history(figure_checkpoint)
        return self

    def load(self, path):
        from joblib import load
        from keras.models import load_model

        model_checkpoint, history_checkpoint, _ = self._get_checkpoint_path(path)
        self.model_ = load_model(model_checkpoint)
        self.history_ = load(history_checkpoint)
        return self

    def _get_checkpoint_path(self, path):
        model_checkpoint = os.path.join(path, self._model_checkpoint)
        figure_checkpoint = os.path.join(path, self._figure_checkpoint)
        history_checkpoint = os.path.join(path, self._history_checkpoint)
        return model_checkpoint, history_checkpoint, figure_checkpoint

    def visualize_history(self, fig_path=None):

        # we need to explicitly configure matplotlib's backend to prevent error when saving figure
        # https://stackoverflow.com/questions/21784641/installation-issue-with-matplotlib-python
        import matplotlib
        matplotlib.use('TkAgg')

        import matplotlib.pyplot as plt

        history = self.history_
        plt.figure(figsize=(12, 8))
        plt.plot(history['loss'], label='Train')
        plt.plot(history['val_loss'], label='Test')
        plt.title('Loss History')
        plt.legend(loc='upper right', fontsize=12)
        if fig_path is not None:
            plt.savefig(fig_path)
        else:
            plt.show()
