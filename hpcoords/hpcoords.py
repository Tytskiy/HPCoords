"""Модуль со всеми реализациями графиков(пользовательское API)"""
from . import utils
from ._core import LinePlotter, SplinePlotter, BaseDataHadler


def parallel_coordinates(data, hue=None, columns=None, directions=None,
                         figsize=(9, 4), spline=False, bundling_coef=None, **kwargs):
    handler = BaseDataHadler()
    columns = handler.required_columns(data, hue, columns)
    dim = columns.size
    directions = handler.get_directions(directions, dim)

    colors, pallete = utils.get_colors(data, hue)
    lower_lim, upper_lim = utils.get_limits(data[columns])

    if spline:# Лучше перенести выбор метода в другой модуль
        plotter = SplinePlotter()
    else:
        plotter = LinePlotter()

    plotter.create_figure(columns, dim, directions, bundling_coef,  lower_lim, upper_lim, figsize)

    for color in pallete:  # Лучше вынести в класс
        color_mask = (colors == color).all(axis=1)
        cluster = data[columns].iloc[color_mask, :]
        plotter.plot_chain(cluster, color, **kwargs)

    return plotter.fig, plotter.axes, plotter.ax_twin
