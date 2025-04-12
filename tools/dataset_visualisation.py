'''
#
# This file contains function for visualization of the dataset and final results
#
'''
from typing import Any
import numpy as np
from numpy.typing import NDArray
from matplotlib import figure, axes
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import pandas as pd

def initial_dataset_display(customers: NDArray[Any],
                            services: NDArray[Any],
                            max_range: int | float,
                            x_range: tuple[int | float, int | float] | list[int | float],
                            y_range: tuple[int | float, int | float] | list[int | float],
                            colors: tuple[str, str],
                            alphas: tuple[float | int, float | int],
                            markers: tuple[str, str],
                            title: str,
                            toggle_ranges: bool = False
                            ) -> tuple[figure.Figure, axes.Axes]:
    '''
    This function displays the initially generated dataset with the service with the option to display their ranges
    '''
    
    # Setup the graph
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
    
    ax.set_title(title)
    ax.set_aspect('equal')

    # If the ranges are toggled expand the plot limits to display the whole circles    
    if toggle_ranges:
        ax.set_ylim(y_range[0] - max_range - 1, y_range[1] + max_range + 1)
        ax.set_xlim(x_range[0] - max_range - 1, x_range[1] + max_range + 1)
    else:
        ax.set_ylim(y_range[0] - 1, y_range[1] + 1)
        ax.set_xlim(x_range[0] - 1, x_range[1] + 1)
    
    # Place the customers and service centers on the plot
    ax.scatter(customers[:, 0], customers[:, 1], color=colors[0], alpha=alphas[0], marker=markers[0])
    ax.scatter(services[:, 0], services[:, 1], color=colors[1], alpha=alphas[1], marker=markers[1])
    
    # Place the service centre ranges if desired
    if toggle_ranges:
        for center in services:
            circle = patch.Circle(xy=(center[0], center[1]),
                                  radius=max_range,
                                  color=colors[1],
                                  alpha=alphas[1],
                                  fill=False,
                                  linewidth=2)
            ax.add_patch(circle)
    
    plt.tight_layout()
    plt.show()
    
    return (fig, ax)