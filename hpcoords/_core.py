"""Основые функциональные единицы библиотеки"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy.interpolate import CubicSpline


class BaseDataHadler:
    def __init__(self):
        pass

    def required_columns(self, data, hue, columns):
        col = data.columns
        if columns is not None:
            col = np.array(columns)

        if hue is not None:
            index = np.argwhere(col == hue)
            if index.size:
                col = np.delete(col, index)
        return col


class BasePlotter:
    def __init__(self):
        self.dim = None
        self.directions = None
        self.lower_lim = None
        self.upper_lim = None
        self.columns = None
        self.figsize = None
        self.fig = None
        self.axes = None
        self.ax_twin = None

    def create_figure(self, columns, dim, directions, lower_lim, upper_lim, figsize):
        self.directions = directions
        self.dim = columns.size
        self.lower_lim = lower_lim
        self.upper_lim = upper_lim
        self.columns = columns
        self.figsize = figsize

        fig, axes = plt.subplots(1, dim-1, figsize=figsize)
        fig.subplots_adjust(wspace=0)
        for i, ax in enumerate(axes):
            ax.spines['top'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.xaxis.set_major_locator(ticker.FixedLocator([0]))
            ax.xaxis.set_major_formatter(ticker.FixedFormatter([columns[i]]))
            ax.set_xlim([0, 1])

            ax.set_ylim([lower_lim[i], upper_lim[i]])

            if self.directions[i] == -1:
                ax.invert_yaxis()

            ax.grid(False)  # Возможно не понадобится

        ax_twin = plt.twinx(axes[-1])
        ax_twin.spines['top'].set_visible(False)
        ax_twin.spines['bottom'].set_visible(False)
        ax_twin.xaxis.set_major_locator(ticker.FixedLocator([0, 1]))
        ax_twin.xaxis.set_major_formatter(ticker.FixedFormatter([columns[-2], columns[-1]]))
        ax_twin.set_ylim([lower_lim[-1], upper_lim[-1]])

        if self.directions[-1] == -1:
            ax_twin.invert_yaxis()

        ax_twin.set_xlim([0, 1])
        ax_twin.grid(False)  # Возможно не понадобится

        self.fig = fig
        self.axes = axes
        self.ax_twin = ax_twin


class LinePlotter(BasePlotter):
    def plot_chain(self, data, color, **kwargs):
        for i in range(self.dim-1):
            subspace = data.iloc[:, i:i+2].values
            self._plot_segments(
                self.axes[i],
                subspace, self.directions[i:i+2],
                self.lower_lim[i: i + 2],
                self.upper_lim[i: i + 2],
                color=color, **kwargs
            )

    def _prepoccessing_directions(self, data, directions, lower_lim, upper_lim):
        y_relative = (data-lower_lim)/(upper_lim-lower_lim)
        y_relative = (directions == [-1, -1])*(1-y_relative) + (directions == [1, 1])*y_relative
        return y_relative

    def _plot_segments(self, ax, data, directions, lower_lim, upper_lim, color, **kwargs):
        x_coords = np.vstack((np.zeros(data.shape[0]), np.ones(data.shape[0])))
        y_relative = self._prepoccessing_directions(data, directions, lower_lim, upper_lim)

        ax.plot(x_coords, y_relative.T, transform=ax.transAxes, c=color, **kwargs)


class SplinePlotter(LinePlotter):
    def _plot_segments(self, ax, data, directions,
                       lower_lim, upper_lim, color, lin_num=20, bc_type=((1, 0), (1, 0)), **kwargs):

        x_coords = np.repeat(np.linspace(0, 1, lin_num)[None, :], data.shape[0], axis=0)

        y_relative = self._prepoccessing_directions(data, directions, lower_lim, upper_lim)
        y_spline = np.apply_along_axis(lambda x: CubicSpline([0, 1], x, bc_type=bc_type)(x_coords[0]),
                                       axis=1, arr=y_relative)
        ax.plot(x_coords.T, y_spline.T, transform=ax.transAxes, c=color, **kwargs)
