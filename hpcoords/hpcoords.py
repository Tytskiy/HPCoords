"""Модуль со всеми реализациями графиков(пользовательское API)"""
import numpy as np
from . import utils
from ._core import LinePlotter, SplinePlotter, BaseDataHadler


def parallel_coordinates(data, hue=None, columns=None, directions=None,
                         figsize=(9, 4), spline=False, **kwargs):
    handler = BaseDataHadler()
    columns = handler.required_columns(data, hue, columns)
    dim = columns.size
    colors, pallete = utils.get_colors(data, hue)
    lower_lim, upper_lim = utils.get_limits(data[columns])

    if spline:
        plotter = SplinePlotter()
    else:
        plotter = LinePlotter()

    if directions is None:  # НАДО ПЕРЕНЕСТИ
        directions = np.ones(dim)
    directions = np.asarray(directions)

    plotter.create_figure(columns, dim, directions, lower_lim, upper_lim, figsize)

    for color in pallete:
        color_mask = (colors == color).all(axis=1)
        cluster = data[columns].iloc[color_mask, :]
        plotter.plot_chain(cluster, color, **kwargs)

    return plotter.fig, plotter.axes, plotter.ax_twin
