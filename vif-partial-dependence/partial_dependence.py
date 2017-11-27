import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


__all__ = ['PartialDependenceExplainer']


class PartialDependenceExplainer:
    """
    References
    ----------
    https://github.com/SauceCat/PDPbox
    """

    def __init__(self, estimator, n_grid_points = 10):
        self.estimator = estimator
        self.n_grid_points = n_grid_points

    def fit(self, data, feature):
        # check whether it's a classification or regression model
        estimator = self.estimator
        try:
            n_classes = estimator.classes_.size
            classifier = True
            predict = estimator.predict_proba
        except AttributeError:
            n_classes = 0
            classifier = False
            predict = estimator.predict

        features = data.columns
        target = data[feature]
        unique_target = np.unique(target)
        n_unique = unique_target.size

        # TODO : can we just specify whether this is a numerical or categorical column
        if n_unique > 2:
            feature_type = 'numerical'
            if self.n_grid_points >= n_unique:
                feature_grid = unique_target
            else:
                percentile = np.percentile(target, np.linspace(0, 100, self.n_grid_points))
                feature_grid = np.unique(percentile)

            feature_cols = feature_grid
        else:
            feature_type = 'categorical'
            feature_grid = unique_target
            feature_cols = ['{}_{}'.format(feature, category) for category in unique_target]

        # compute prediction chunk by chunk to save memory usage
        results = []
        n_rows = data.shape[0]
        chunk_size = int(n_rows / feature_grid.size)

        # TODO :
        # embarrassingly parrallelized problem, can parallelize this if it becomes a bottleneck
        for i in range(0, n_rows, chunk_size):
            # generate ice (individual conditional expectation) data
            data_chunk = data[i:i + chunk_size]
            ice_chunk = np.repeat(data_chunk.values, repeats = feature_grid.size, axis = 0)
            ice_data = pd.DataFrame(ice_chunk, columns = features)
            ice_data[feature] = np.tile(feature_grid, data_chunk.shape[0])

            prediction = predict(ice_data)
            if classifier:
                result = prediction[:, 1]
            else:
                result = prediction

            # reshape tiled data back to original chunk's shape
            reshaped = result.reshape((data_chunk.shape[0], feature_grid.size))
            result = pd.DataFrame(reshaped, columns = feature_cols)
            results.append(result)

        # add original prediction and column's value ??
        self.feature_name_ = feature
        self.feature_grid_ = feature_grid
        self.feature_type_ = feature_type
        self.feature_cols_ = feature_cols
        results = pd.concat(results)
        return results

    def plot(self, results, center = True):
        gs = GridSpec(5, 1)
        ax1 = plt.subplot(gs[0, :])
        self._plot_title(ax1)
        ax2 = plt.subplot(gs[1:, :])
        self._plot_content(ax2, results, center)

    def _plot_title(self, ax):
        font_family = 'Arial'
        title = 'Individual Conditional Expectation Plot for {}'.format(self.feature_name_)
        subtitle = 'Number of unique grid points: {}'.format(self.feature_grid_.size)
        title_fontsize = 15
        subtitle_fontsize = 12

        ax.set_facecolor('white')
        ax.text(
            0, 0.7, title,
            fontsize = title_fontsize, fontname = font_family)
        ax.text(
            0, 0.4, subtitle, color = 'grey',
            fontsize = subtitle_fontsize, fontname = font_family)
        ax.axis('off')

    def _plot_content(self, ax, results, center):

        # pd (partial dependence)
        pd_linewidth = 2
        pd_markersize = 5
        pd_color = '#1A4E5D'
        fill_alpha = 0.2
        fill_color = '#66C2D7'
        zero_linewidth = 1.5
        zero_color = '#E75438'
        xlabel_fontsize = 10

        self._modify_axis(ax)
        if self.feature_type_ == 'categorical':
            # ticks = all the unique categories
            x = range(len(self.feature_cols_))
            ax.set_xticks(x)
            ax.set_xticklabels(self.feature_cols_)
        else:
            x = self.feature_cols_

        # center the partial dependence plot by subtacting every value
        # with the value of the first column, i.e. first column's value
        # will serve as the baseline (centered at 0) for all other values
        # https://stackoverflow.com/questions/43770401/subtract-pandas-columns-from-a-specified-column
        if center:
            results = results.copy()
            center_col = self.feature_cols_[0]
            results = results[self.feature_cols_].sub(results[center_col], axis = 0)

        pd = results.values.mean(axis = 0)
        pd_std = results.values.std(axis = 0)
        upper = pd + pd_std
        lower = pd - pd_std

        ax.plot(
            x, pd, color = pd_color, linewidth = pd_linewidth,
            marker = 'o', markersize = pd_markersize)
        ax.plot(
            x, [0] * pd.size, color = zero_color,
            linestyle = '--', linewidth = zero_linewidth)
        ax.fill_between(x, upper, lower, alpha = fill_alpha, color = fill_color)
        ax.set_xlabel(self.feature_name_, fontsize = xlabel_fontsize)

    def _modify_axis(self, ax):
        tick_labelsize = 8
        tick_colors = '#9E9E9E'
        tick_labelcolor = '#424242'

        ax.tick_params(
            axis = 'both', which = 'major', colors = tick_colors,
            labelsize = tick_labelsize, labelcolor = tick_labelcolor)

        ax.set_facecolor('white')
        ax.get_yaxis().tick_left()
        ax.get_xaxis().tick_bottom()
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(True, 'major', 'x', ls = '--', lw = .5, c = 'k', alpha = .3)
        ax.grid(True, 'major', 'y', ls = '--', lw = .5, c = 'k', alpha = .3)
