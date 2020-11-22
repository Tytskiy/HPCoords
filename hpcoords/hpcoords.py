"""Основной модуль со всеми реализациями графиков"""
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
import seaborn as sn

# Пока что сделал так, но позже надо будет перенести всю предобработку данных в отдельный модуль,
#  возможно будет удобно инкапсулировать все данные в некотором классе


def get_labels_colors(labels):
    uniq = labels.unique()
    colors = dict(zip(uniq, sn.color_palette(n_colors=uniq.shape[0])))
    rgb_labels = labels.apply(lambda x: colors[x]).values
    return rgb_labels


def get_colors(data, hue, c):
    if c is not None:
        return c

    if hue is None:
        colors = sn.color_palette(n_colors=1)*data.shape[0]
    else:
        colors = get_labels_colors(data[hue])
    return colors


def required_columns(data, hue, columns):
    col = data.columns
    if columns is not None:
        col = np.array(columns)

    if hue is not None:
        index = np.argwhere(col == hue)
        if index.size:
            col = np.delete(col, index)
    return col


def parallel_coordinates(data, hue=None, columns=None, c=None, figsize=(9, 4), ** kwargs):
    columns = required_columns(data, hue, columns)
    dim = columns.size
    colors = get_colors(data, hue, c)

    fig, axes = plt.subplots(1, dim-1, figsize=figsize)
    fig.subplots_adjust(wspace=0)

    delta = 0.2
    min_values = data[columns].min(axis=0).values
    max_values = data[columns].max(axis=0).values
    min_values -= (max_values-min_values)*delta
    max_values += (max_values-min_values)*delta
    print(min_values, max_values)
    for i, ax in enumerate(axes):
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.xaxis.set_major_locator(ticker.FixedLocator([0]))
        ax.xaxis.set_major_formatter(ticker.FixedFormatter([columns[i]]))
        ax.set_xlim([0, 1])
        ax.set_ylim([min_values[i], max_values[i]])
        ax.grid(False)

    ax_twin = plt.twinx(axes[-1])
    ax_twin.spines['top'].set_visible(False)
    ax_twin.spines['bottom'].set_visible(False)
    ax_twin.xaxis.set_major_locator(ticker.FixedLocator([0, 1]))
    ax_twin.xaxis.set_major_formatter(ticker.FixedFormatter([columns[-2], columns[-1]]))
    ax_twin.set_ylim([min_values[-1], max_values[-1]])
    ax_twin.set_xlim([0, 1])

    ax_twin.grid(False)
    x_coords = [0, 1]
    for i in range(dim-1):
        y_coords = data[columns].iloc[:, i:i+2].values
        y_coords_relative = (y_coords-min_values[i:i+2])/(max_values[i:i+2]-min_values[i:i+2])
        for j, c in enumerate(colors):
            axes[i].plot(x_coords, y_coords_relative[j],
                         transform=axes[i].transAxes, c=c, **kwargs)
    return fig, axes
