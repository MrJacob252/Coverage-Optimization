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
import seaborn as sns
from matplotlib.colors import ListedColormap
import matplotlib

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

def heatmap(data: pd.DataFrame) -> tuple[figure.Figure, axes.Axes]:
    '''
    Displays heatmap of the used capacities with services being on the X axis and customers on the Y\n
    Expected format of the DataFrame: [Unnamed (index), X, Y, value] if loaded from .csv or
    [X, Y, value] if used straight from GAMSpy results
    '''
    
    data_frame = data.copy()
    
    # Extract the labels
    if len(data_frame.columns) == 4:
        x_lab, y_lab, value_lab = data_frame.columns[1:4]
    else:
        x_lab, y_lab, value_lab = data_frame.columns[:3]
    
    
    # Pivot the dataset to have matrix like structure
    heatmap_data = data_frame.pivot(index=x_lab, columns=y_lab, values=value_lab)
    
    # Create annotation heatmap that will not display values of 0
    annotations = heatmap_data.copy()
    
    def clean_annotation(x) -> str:
        result = str(int(x)) if int(x) > 0 else ""
        return result
        
    annotations = annotations.map(clean_annotation)
    
    # Create custom colormap
    # zero_color = "#FF5953"
    zero_color = "#4D0055"
    base_colormap = matplotlib.colormaps["viridis"]
    
    # Create custom colormap list with the custom zero color being at the lowest slot and the other colors
    # taken from the default colormap
    colors = [zero_color] + [base_colormap(i) for i in np.linspace(0, 1, 256)]
    custom_colormap = ListedColormap(colors)
    
    
    # Plot the data
    fig, ax = plt.subplots(nrows=1, ncols=1)
    
    sns.heatmap(heatmap_data,
                ax=ax,
                annot=annotations,
                cmap=custom_colormap,
                fmt="",     # This needs to be empty because the annotations are doing the formatting
                # linewidths=0.5,
                linecolor="white")
    
    ax.set_title("Heatmap")
    ax.set_xlabel(y_lab)
    ax.set_ylabel(x_lab)
    
    return (fig, ax)
    

if __name__== "__main__":
    pass

    P_data = pd.read_csv("./src/tools/tmp/results/P_data.csv", sep=";")
    X_data = pd.read_csv("./src/tools/tmp/results/X_data.csv", sep=";")
    
    
    print(f"XS: {sum(X_data["selected"] != 0)}")
    
    fig, ax = heatmap(P_data)
    
    plt.show()

