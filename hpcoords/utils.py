"""Вспомогательные функции логически не относящиеся к основной функциональности"""
import numpy as np
import seaborn as sn


def get_labels_colors(labels=None):
    uniq = np.sort(labels.unique())
    pallete = sn.color_palette(n_colors=uniq.shape[0])

    colors = dict(zip(uniq, pallete))
    rgb_labels = labels.apply(lambda x: colors[x]).values
    return np.vstack(rgb_labels), pallete


def get_colors(data, hue):
    if hue is None:
        pallete = sn.color_palette(n_colors=1)
        rgb_labels = np.asarray(pallete*data.shape[0])
    else:
        rgb_labels, pallete = get_labels_colors(data[hue])
    return rgb_labels, pallete


def get_limits(data, delta=0.2):
    lower_lim = data.min(axis=0).values
    upper_lim = data.max(axis=0).values
    lower_lim -= (upper_lim-lower_lim)*delta
    upper_lim += (upper_lim-lower_lim)*delta
    return lower_lim, upper_lim
