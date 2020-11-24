"""Модуль со всеми реализациями графиков(пользовательское API)"""
import utils
from _core import LinePlotter, BaseDataHadler


def parallel_coordinates(data, hue=None, columns=None, figsize=(9, 4), ** kwargs):

    handler = BaseDataHadler()
    columns = handler.required_columns(data, hue, columns)

    dim = columns.size
    colors, pallete = utils.get_colors(data, hue)
    lower_lim, upper_lim = utils.get_limits(data[columns])

    plotter = LinePlotter()
    plotter.create_figure(columns, dim, lower_lim, upper_lim, figsize)

    for color in pallete:
        color_mask = (colors == color).all(axis=1)
        cluster = data[columns].iloc[color_mask, :]
        plotter.plot_chain(cluster, color, **kwargs)

    return plotter.fig, plotter.axes, plotter.ax_twin
