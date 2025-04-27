'''
#
# This file contains function for visualization of the dataset and final results
#
'''
from typing import Any
import matplotlib.axes
import numpy as np
from numpy.typing import NDArray
from matplotlib import figure, axes
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import pandas as pd
import seaborn as sns
from matplotlib.colors import ListedColormap
import matplotlib
import networkx as nx
from  mpl_toolkits.axes_grid1.inset_locator import inset_axes

import src.tools.load_data as load 

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
    
def color_the_centers(X_results: pd.DataFrame,
                      service_dataset: pd.DataFrame,
                      service_matrix: NDArray[Any]) -> pd.DataFrame:
    '''
    Adds colors for the service center for better visualization
    Returns a dataframe that only contains the selected centers and has new column for
    the graph color
    '''
    
    colored_data = service_dataset.copy()
    
    colored_data = colored_data[X_results["selected"] == 1]
    
    # Create a graph and add nodes to it
    Graph = nx.Graph()
    for index in colored_data.index:
        Graph.add_node(index)
    
    # Add vertexes between nodes that are in range of each other
    ranges = service_dataset["range"].values
    n_nodes = len(colored_data)
    
    for i in range(n_nodes):
        i_index = int(colored_data.index[i])
        # No need to go through the previous nodes
        for j in range(i + 1, n_nodes):
            j_index = int(colored_data.index[j])
            # if service_matrix[i_index, j_index] <= ranges[i_index] or service_matrix[i_index, j_index] <= ranges[j_index]:
            if service_matrix[i_index, j_index] <= ranges[i_index] + ranges[j_index]:
                   Graph.add_edge(i_index, j_index)
            pass
        
    # Color the graph
    coloring = nx.coloring.greedy_color(Graph)
    colored_data["color"] = colored_data.index.map(coloring)
    
    # print(colored_data)
    
    return colored_data

def plot_the_results(colored_results: pd.DataFrame,
                     customer_dataset: pd.DataFrame,
                     P_data: pd.DataFrame,
                     color_list: list[str],
                     x_range: tuple[int | float, int | float] | list[int | float],
                     y_range: tuple[int | float, int | float] | list[int | float],
                     toggle_ranges: bool = True) -> tuple[figure.Figure, axes.Axes]:
    '''
    Plots the selected and colored service centers and plots customers as tiny 
    pie charts to show which service centers covers them 
    '''
    # TODO: 
    # - [ ] Cross size parameter
    # - [ ] Customer size parameter
    # - [ ] (maybe some visualisation config struct again)
    # - [ ] Service ranges toggle
    
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20, 20))
    
    ax.set_title("Results")
    ax.set_aspect("equal")
    
    max_range = int(max(colored_results["range"]))
    
    if toggle_ranges:
        ax.set_ylim(y_range[0] - max_range - 1, y_range[1] + max_range + 1)
        ax.set_xlim(x_range[0] - max_range - 1, x_range[1] + max_range + 1)
    else:
        ax.set_ylim(y_range[0] - 1, y_range[1] + 1)
        ax.set_xlim(x_range[0] - 1, x_range[1] + 1)
    
    customers_x = customer_dataset["x"]
    customers_y = customer_dataset["y"]    
    
    service_x = colored_results["x"].values
    service_y = colored_results["y"].values
    service_color = colored_results["color"].values
    service_ranges = colored_results["range"].values
    
    # TODO: There is some bug with the colors that sometimes triggers (maybe more colors needed?)
    for i in range(len(service_x)):
        ax.scatter(service_x[i], service_y[i], color=color_list[service_color[i]], alpha=1, marker="+", s=100)
        
        circle = patch.Circle(xy=(service_x[i], service_y[i]),
                              radius=service_ranges[i],
                              color=color_list[service_color[i]],
                              alpha=0.5,
                              fill=False,
                              linewidth=2)
        ax.add_patch(circle)
    
    # Place customers
    
    # Basic customers, only as points
    # ax.scatter(customers_x, customers_y, color="blue", alpha=1, marker=".")
    
    # Plot the pie charts
    
    # P_data.loc[(P_data["value"] > 0) & (P_data["I"] == 4), "J"].values <- will return which services contributed (number is +1)
    
    # # ===================================== DRAWING USING INSET AXES
    # # Size will stay the same when zooming in
    # # size of the chart
    # size = 0.25
    # for i in range(len(customers_x)):
    #     inset_ax = inset_axes(ax, width=size, height=size, loc="center",
    #                         bbox_to_anchor=(customers_x[i], customers_y[i]),
    #                         bbox_transform=ax.transData,
    #                         borderpad=0)
        
    #     # Inset the pie chart: Query the data  
    #     service_centers_covering = P_data.loc[(P_data["value"] > 0) & (P_data["I"] == (i + 1)), "J"].values
    #     service_centers_contribution = P_data.loc[(P_data["value"] > 0) & (P_data["I"] == (i + 1)), "value"].values
    #     service_centers_colors = []
        
    #     for center in service_centers_covering:
    #         service_centers_colors.extend(np.array(colored_results.loc[colored_results.index == (center - 1), "color"]))
        
    #     inset_ax.pie(service_centers_contribution,
    #                  colors=[color_list[service_centers_colors[c]] for c in range(len(service_centers_colors))])    
    # # =================================================================
    
    # ===================================== DRAWING USING WEDGES
    # Manually placed pie chart slices that will have fixed size and will zoom in and out
    radius = 2
    for i in range(len(customers_x)):
        
        # Query data from the result dataframe
        service_centers_covering = P_data.loc[(P_data["value"] > 0) & (P_data["I"] == (i + 1)), "J"].values
        service_centers_contribution = P_data.loc[(P_data["value"] > 0) & (P_data["I"] == (i + 1)), "value"].values
        
        # Create list of colors numbers for the contributing service centers
        service_centers_colors = []
        for center in service_centers_covering:
            service_centers_colors.extend(np.array(colored_results.loc[colored_results.index == (center - 1), "color"]))

        # Calculate "percentage" of how much each service center contributes to the whole customer
        contribution_fractions = [(s / sum(service_centers_contribution)) for s in service_centers_contribution]
        # Create list of color codes/names base on the color numbers
        mapped_colors = [color_list[service_centers_colors[c]] for c in range(len(service_centers_colors))]

        # Place all the wedges of the pie chart
        start_angle = 0 # Angle from where to start drawing
        for fraction, color in zip (contribution_fractions, mapped_colors):
            angle = 360 * fraction
            wedge = patch.Wedge(center=(customers_x[i], customers_y[i]),
                                r=radius,
                                theta1=start_angle,
                                theta2=start_angle + angle,
                                facecolor=color,
                                #edgecolor="black"
                                )
            ax.add_patch(wedge)
            start_angle += angle
            
        
    plt.show()
    
    return (fig, ax)

def __test():
    pass

    P_data = pd.read_csv("./src/tools/tmp/results/P_data.csv", sep=";")
    X_data = pd.read_csv("./src/tools/tmp/results/X_data.csv", sep=";")
    services = pd.read_csv("./src/tools/tmp/test_dataset_1_service.csv", sep=";")
    customers = pd.read_csv("./src/tools/tmp/test_dataset_1_customers.csv", sep=";")
    
    
    ##### Heatmap test 
    # print(f"XS: {sum(X_data["selected"] != 0)}")
    
    # fig, ax = heatmap(P_data)
    
    # plt.show()
    ##### Heatmap test end
    
    ##### Visualization test
    service_loc, _, _, _ = load.load_service("./src/tools/tmp/test_dataset_1_service.csv", ".csv")
    customer_loc, customer_cap, = load.load_customers("./src/tools/tmp/test_dataset_1_customers.csv", ".csv")
    
    distance_matrix = load.create_distance_matrix(service_loc, service_loc, 0)
    
    colored_data = color_the_centers(X_data, services, distance_matrix)

    color_list = ["Blue", "Red", "Green", "Purple", "Magenta", "Orange"]
    hex_colors = [
        '#e61919',  # Bright Red
        '#1a80f2',  # Strong Blue
        '#26bf33',  # Vivid Green
        '#ff9900',  # Orange
        '#a633cc',  # Purple
        '#f2cc1a',  # Golden Yellow
    ]


    plot_the_results(colored_results=colored_data,
                     customer_dataset=customers,
                     P_data=P_data,
                    #  color_list=color_list,
                     color_list=hex_colors,
                     x_range=(0, 100),
                     y_range=(0, 100),
                     toggle_ranges=True)

if __name__== "__main__":
    __test()