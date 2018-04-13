"""
Keras callback for learning rate finder and cyclical learning rate.

References
----------
https://github.com/bckenstler/CLR
https://github.com/metachi/fastaiv2keras/blob/master/fastai/utils.py
"""
import os
import numpy as np
from keras import backend as K
from keras.callbacks import Callback
from matplotlib import pyplot as plt


class LRUpdate(Callback):
    """
    This callback is utilized to log the learning rates for every iteration (batch cycle
    i.e. dataset size / batch size). It is not meant to be directly used as a callback
    but extended by other callbacks ie. LRFind, LRCycle
    """

    def __init__(self):
        super().__init__()

        # placed at __init__ instead of on_train_begin
        # so the record doesn't get deleted when user
        # is doing continuous training from a checkpoint
        self.history = {}
        self.trained_iterations = 0

    def _get_lr(self):
        """
        Modify the method to change the learning rate behavior
        during each iteration.
        """
        return K.get_value(self.model.optimizer.lr)

    def on_train_begin(self, logs = None):
        logs = logs or {}

        # initialize proper learning rates
        # handle edge case of multiple learning rates
        lr_shape = K.get_variable_shape(self.model.optimizer.lr)
        if len(lr_shape) > 0:
            self.min_lr = np.full(lr_shape, self._get_lr())

        K.set_value(self.model.optimizer.lr, self.min_lr)

    def on_batch_end(self, batch, logs = None):
        logs = logs or {}
        self.trained_iterations += 1
        K.set_value(self.model.optimizer.lr, self._get_lr())
        self.history.setdefault('lr', []).append(K.get_value(self.model.optimizer.lr))
        self.history.setdefault('iterations', []).append(self.trained_iterations)
        for k, v in logs.items():
            self.history.setdefault(k, []).append(v)

    def plot_lr(self):
        """Plot the learning rate (y-axis) versus for each iteration (x-axis)"""
        plt.xlabel('iterations')
        plt.ylabel('learning rate')
        plt.plot(self.history['iterations'], self.history['lr'])


class LRFind(LRUpdate):
    """
    Callback that helps determine the optimal learning rate for the current model.

    Parameters
    ----------
    iterations : int
        Batch cycle, calculated by training dataset size // batch size.

    min_lr : float, default 1e-5
        Lower bound of learning rate.

    max_lr : float, default 10
        Upper bound of learning rate.

    jump : int, default 6
        x-fold loss increase that will cause training to stop.
    """

    def __init__(self, iterations, min_lr = 1e-5, max_lr = 10, jump = 6):
        super().__init__()
        self.jump = jump
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.iterations = iterations
        self.lr_mult = (max_lr / min_lr) ** (1 / iterations)

        # save the weights, so we can reset the model to its original
        # state, i.e. the weights before running the LRFind, the saved
        # weight will be deleted
        self._temp_weight_path = 'tmp.h5'

    def _get_lr(self):
        return self.min_lr * (self.lr_mult ** self.trained_iterations)

    def on_train_begin(self, logs = None):
        super().on_train_begin(logs = logs)
        self.best = 1e9
        self.model.save_weights(self._temp_weight_path)
        self.original_lr = K.get_value(self.model.optimizer.lr)

    def on_batch_end(self, batch, logs = None):
        """Check if we have made an x-fold jump in loss and training should stop."""
        super().on_batch_end(batch, logs = logs)
        loss = self.history['loss'][-1]
        if np.isnan(loss) or loss > self.best * self.jump:
            self.model.stop_training = True
        if loss < self.best:
            self.best = loss

    def on_train_end(self, logs = None):
        """
        We've modified the model's learning rate and weights during
        this process, here we revert back to model's original state.
        """
        self.model.load_weights(self._temp_weight_path)
        os.remove(self._temp_weight_path)
        K.set_value(self.model.optimizer.lr, self.original_lr)

    def plot_loss(self):
        """Plot the loss (y-axis) versus for each log-scaled learning rate (x-axis)"""
        plt.xlabel('learning rate (log scale)')
        plt.ylabel('loss')
        plt.plot(self.history['lr'], self.history['loss'])
        plt.xscale('log')


class LRCycle(LRUpdate):
    """
    This callback implements the triangle2 cyclical learning rate policy (CLR) [1]_.
    The method cycles the learning rate between two boundaries with a triangle
    pattern that decreases the amplitude by half after each period, while keeping
    the base learning rate constant.

    Parameters
    ----------
    min_lr : float, default 1e-5
        Lower bound of learning rate

    max_lr : float, default 10
        Upper bound of learning rate

    step_size : int, default 250
        Number of training iterations per half cycle. Authors suggest
        setting step_size in the range of 2-8x training iterations in epoch.

    References
    ----------
    .. [1] `L. Smith - Cyclical Learning Rates for Training Neural Networks (2017)
            <https://arxiv.org/abs/1506.01186>`_
    """
    def __init__(self, min_lr = 1e-5, max_lr = 10, step_size = 250):
        super().__init__()
        self.min_lr = min_lr
        self.max_lr = max_lr
        self.step_size = step_size

    def _get_lr(self):
        cycle = np.floor(1 + self.trained_iterations / (2 * self.step_size))
        x = np.abs(self.trained_iterations / self.step_size - 2 * cycle + 1)
        triangle_scaling = np.maximum(0, (1 - x)) / (2 ** (cycle - 1))
        return self.min_lr + (self.max_lr - self.min_lr) * triangle_scaling
