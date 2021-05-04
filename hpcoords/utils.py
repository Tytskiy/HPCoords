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


class Z_plane:
    "z=ax+by+c"

    def __init__(self, x, y):
        self.a, self.b, self.c = y[0]-y[1], x[1]-x[0], x[0]*y[1]-x[1]*y[0]

    def __call__(self, x, y):
        return self.a*x+self.b*y[:, None]+self.c

    def get_y(self, x):
        return -(self.a*x+self.c)/self.b


def alpha_interpolate(x, y, upper, middle, lower, max_alpha=1, coef_decrease=1, **kwargs):
    upper_value = max_alpha*(1-coef_decrease*middle(x, y)/(upper.get_y(x)-middle.get_y(x)))
    upper_value[upper_value <= 0] = 0
    upper_value[upper_value > max_alpha] = 0

    lower_value = max_alpha*(1+coef_decrease*middle(x, y)/(middle.get_y(x)-lower.get_y(x)))
    lower_value[lower_value <= 0] = 0
    lower_value[lower_value >= max_alpha] = 0
    return (upper_value + lower_value)**coef_decrease
