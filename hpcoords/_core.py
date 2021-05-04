"""Основые функциональные единицы библиотеки"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from scipy.interpolate import CubicSpline
from matplotlib.patches import Polygon
from .utils import Z_plane, alpha_interpolate


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

    def _plot_segments(self, ax, data, directions, lower_lim, upper_lim, color, **kwargs):
        pass

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


class LinePlotter(BasePlotter):
    def __init__(self):
        self.bundling_coef = None
        super().__init__()

    def create_figure(self, columns, dim, directions, bundling_coef, lower_lim, upper_lim, figsize):
        self.bundling_coef = bundling_coef
        super().create_figure(columns, dim, directions, lower_lim, upper_lim, figsize)

    def _prepoccessing(self, data, directions, lower_lim, upper_lim):

        x = np.hstack((np.zeros(data.shape[0])[:, None], np.ones(data.shape[0])[:, None]))
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
        return x, y  # Вдоль оси 0 объекты, вдоль оси 1 координаты

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


class AggregatePlotter(BasePlotter):
    def __init__(self):
        self.aggregate = None
        self.func_aggregate = None
        self.max_alpha = None
        self.coef_decrease = None
        super().__init__()

    def create_figure(self, columns, dim, directions, aggregate, lower_lim, upper_lim,
                      max_alpha, coef_decrease, figsize):
        self.max_alpha = max_alpha
        self.coef_decrease = coef_decrease
        self.aggregate = aggregate

        if aggregate == "3std":
            self.func_aggregate = np.std
        elif aggregate == "minmax":
            self.func_aggregate = (np.min, np.max)
        else:
            raise ValueError

        super().create_figure(columns, dim, directions, lower_lim, upper_lim, figsize)

    def _prepoccessing(self, data, directions, lower_lim, upper_lim):
        y = (data-lower_lim)/(upper_lim-lower_lim)
        y = (directions == [-1, -1])*(1-y) + (directions == [1, 1])*y
        return y  # Вдоль оси 0 объекты, вдоль оси 1 координаты

    def _plot_segments(self, ax, data, directions, lower_lim, upper_lim, color, **kwargs):
        y_coords = self._prepoccessing(data, directions, lower_lim, upper_lim)

        prev_mean, next_mean = y_coords.mean(axis=0)
        if self.aggregate == "3std":
            prev_agg, next_agg = self.func_aggregate(y_coords, axis=0)
            coords = np.array([[0, prev_mean - 3*prev_agg],
                               [1, next_mean - 3*next_agg],
                               [1, next_mean + 3*next_agg],
                               [0, prev_mean + 3*prev_agg]])
        elif self.aggregate == "minmax":
            prev_min, next_min = self.func_aggregate[0](y_coords, axis=0)
            prev_max, next_max = self.func_aggregate[1](y_coords, axis=0)
            coords = np.array([[0, prev_min],
                               [1, next_min],
                               [1, next_max],
                               [0, prev_max]])

        bbox = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(), coords[:, 1].max())

        src_img = np.zeros((100, 100, 4), dtype=float)
        src_img[:, :, [0, 1, 2]] = np.asarray(color)

        upper_y = np.array([coords[3][1], coords[2][1]])
        middle_y = np.array([prev_mean, next_mean])
        lower_y = np.array([coords[0][1], coords[1][1]])

        upper = Z_plane([0, 1], (upper_y-bbox[2])/(bbox[3]-bbox[2]))
        middle = Z_plane([0, 1], (middle_y-bbox[2])/(bbox[3]-bbox[2]))
        lower = Z_plane([0, 1], (lower_y-bbox[2])/(bbox[3]-bbox[2]))

        disc_x = np.linspace(0, 1, 100)
        disc_y = np.linspace(1, 0, 100)

        src_img[:, :, 3] = alpha_interpolate(
            disc_x, disc_y, upper, middle, lower, self.max_alpha, self.coef_decrease)

        poly = Polygon(coords, fc='none', ec="none", transform=ax.transAxes)
        filler = ax.imshow(src_img, aspect='auto', extent=bbox, transform=ax.transAxes)
        filler.set_clip_path(poly)
        ax.add_patch(poly)
        ax.plot([0, 1], [prev_mean, next_mean], color=color, transform=ax.transAxes, **kwargs)
