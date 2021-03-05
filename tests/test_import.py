import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

from hpcoords import parallel_coordinates

#print(parallel_coordinates)

iris = sns.load_dataset('iris')

plt.style.use("seaborn")

mpl.rcParams["axes.linewidth"] = 1
mpl.rcParams["axes.edgecolor"] = "grey"
mpl.rcParams["ytick.labelsize"] = 12
mpl.rcParams["xtick.labelsize"] = 14

parallel_coordinates(
    iris,
    hue="species",
    spline=True,
    directions=[1, 1, 1, 1],
    bundling_coef=0.1,
    lw=1.5,
    alpha=0.3,
    figsize=(14, 7)
)
plt.show()