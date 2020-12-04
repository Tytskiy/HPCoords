"""Основые функциональные единицы библиотеки"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy.interpolate import CubicSpline, CubicHermiteSpline


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

    def get_directions(self, directions, dim):
        if directions is None:
            directions = np.ones(dim)
        directions = np.asarray(directions)
        return directions


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
    def __init__(self):
        self.bundling_coef = None
        super().__init__()

    def create_figure(self, columns, dim, directions, bundling_coef, lower_lim, upper_lim, figsize):
        self.bundling_coef = bundling_coef
        super().create_figure(columns, dim, directions, lower_lim, upper_lim, figsize)

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

    def _prepoccessing(self, data, directions, lower_lim, upper_lim):

        x = np.vstack((np.zeros(data.shape[0]), np.ones(data.shape[0])))
        if self.bundling_coef is not None:
            mid = np.full(x.shape[1], 0.5)
            x = np.vstack((x[0], mid, x[-1]))

        y = (data-lower_lim)/(upper_lim-lower_lim)
        y = (directions == [-1, -1])*(1-y) + (directions == [1, 1])*y

        if self.bundling_coef is not None:
            coef = self.bundling_coef
            bundle = (y[:, 0]+y[:, -1])/2
            bundle = (bundle-bundle.mean())*coef+bundle.mean()
            y = np.hstack((y[:, 0][:, None], bundle[:, None], y[:, -1][:, None]))
        return x.T, y  # Вдоль оси 0 объекты, вдоль оси 1 координаты

    def _plot_segments(self, ax, data, directions, lower_lim, upper_lim, color, **kwargs):

        x_coords, y_coords = self._prepoccessing(data, directions, lower_lim, upper_lim)
        ax.plot(x_coords.T, y_coords.T, transform=ax.transAxes, c=color, **kwargs)


class SplinePlotter(LinePlotter):
    def _plot_segments(self, ax, data, directions,
                       lower_lim, upper_lim, color, lin_num=20, **kwargs):

        x_coords = np.repeat(np.linspace(0, 1, lin_num)[None, :], data.shape[0], axis=0)

        x_tmp, y_coords = self._prepoccessing(data, directions, lower_lim, upper_lim)
        # Пока что не меняю на HermiteSpline, потому что непонятно какая производная должна быть
        # в середине
        spliner = CubicSpline(x_tmp[0], y_coords, bc_type="clamped", axis=1)
        y_spline = spliner(x_coords[0])
        ax.plot(x_coords.T, y_spline.T, transform=ax.transAxes, c=color, **kwargs)
