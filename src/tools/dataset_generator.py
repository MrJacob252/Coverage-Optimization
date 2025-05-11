'''
#
# This file contains functions for generation and export of the dataset
#
'''

import numpy as np
import pandas as pd
from typing import Literal, Any
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import scipy as sc
from scipy.stats import qmc
from numpy.typing import NDArray
from datetime import datetime
import pathlib
from dataclasses import dataclass

from src.tools.dataset_visualisation import initial_dataset_display

@dataclass
class VisualConfig:
    colors: tuple[str, str] = ("blue", "red")
    alphas: tuple[int | float, int | float] = (0.7, 0.5)
    markers: tuple[str, str] = (".", "+")
    

def poisson_disc_random_samples(n_points: int,
                                radius: int | float,
                                x_range: tuple[int, int] | tuple[float, float] | list[int | float],
                                y_range: tuple[int, int] | tuple[float, float] | list[int | float],) -> NDArray[np.float64]:
    '''
    Function fill space given by "x_range" and "y_range" parameters using Poisson disc algorithm with "radius" 
    parameter and then randomly selects "n_points" from this space to use as a dataset
    '''
    
    rng = np.random.default_rng()
    
    # Create the Poisson disc engine
    engine = qmc.PoissonDisk(d=2,
                             radius=radius,
                             rng=rng,
                             optimization=None, # No post-processing
                             l_bounds=(x_range[0], y_range[0]),
                             u_bounds=(x_range[1], y_range[1]))
    
    # Fill the space with samples
    samples = engine.fill_space()
    
    # randomly select n_points points
    selected = np.random.choice(a=len(samples), size=n_points, replace=False)
    samples_selected = np.array([samples[i] for i in selected])
    
    return samples_selected    
    
def service_location_grid_generation(spacing: int | float,
                                     x_range: tuple[int, int] | tuple[float, float] | list[int | float],
                                     y_range: tuple[int, int] | tuple[float, float] | list[int | float],) -> NDArray[Any]:
    '''
    Creates grid of service centres with spaced from each other by the given "spacing" parameter.\n
    Dimensions of the grid specified by the "x_range" and "y_range" parameters
    '''
    
    # Generate the x and y coordinates of the centers
    # stop parameter is the upper bound + spacing to create center on both edges 
    x_coords = np.arange(x_range[0], x_range[1] + spacing, spacing)
    y_coords = np.arange(y_range[0], y_range[1] + spacing, spacing)
    
    # Generate the grid
    x_values, y_values = np.meshgrid(x_coords, y_coords)
    
    # Convert grid to a (N, 2) sized array
    service_locations = np.stack([x_values.ravel(), y_values.ravel()], axis=1)
    
    return service_locations

def customer_demand_generation(n_locations: int,
                               center: int | float,
                               deviation: int | float) -> NDArray[Any]:
    '''
    Function generates random demand value for "n_location" customers using normal distribution specified by the
    "center" (mean) and "deviation" (standard deviation) parameters
    '''
    
    rng = np.random.default_rng()
    
    demand = np.round(rng.normal(loc=center, scale=deviation, size=n_locations))
    
    return demand

def service_capacity_generation(n_locations: int,
                                center: int | float,
                                deviation: int | float) -> NDArray[Any]:
    '''
    Function generates random capacity for each "n_locations" service centers using normal distribution specified by the
    "center" (mean) and "deviation" (standard deviation) parameters
    '''
        
    rng = np.random.default_rng()
    
    capacity = np.round(rng.normal(loc=center, scale=deviation, size=n_locations))
    
    return capacity

def data_save(data: pd.DataFrame,
              file_type: Literal[".csv", ".pkl"],
              location: str | pathlib.Path) -> None:
    '''
    Function saves the data into either .csv or .pkl (specified by the "type" parameter) onto a location 
    specified by the "location" and "file name" parameter.
    '''
    
    match file_type:
        case ".csv":
            data.to_csv(location, sep=";")
        case ".pkl":
            data.to_pickle(location)
    
def create_location_dataframe(locations: NDArray[Any],
                              capacity: NDArray[Any],
                              weight: NDArray[Any] | list[int] | list[float] | None = None,
                              max_range: int | float | None = None) -> pd.DataFrame:
    '''
    Function merges the locations coordinates and capacity/demand values into one DataFrame with 3/4 columns\n
    **X**: x coordinate of the location\n
    **Y**: y coordinate of the location\n
    **Value**: Value of the demand/capacity of the location\n
    **Weight**: Weight of the individual service centers\n
    **Range**: Value of the range of the service location caved only on row 0 and only for service location
    '''
    
    names = ["x", "y", "value", "weight", "range"]
    
    final_frame = pd.DataFrame(locations, columns=names[:2])
    
    final_frame[names[2]] = capacity
    
    # Append weights if provided, else use weight of 1
    if weight is not None:
        final_frame[names[3]] = weight
    
    if max_range is not None:
        final_frame[names[4]] = max_range
    
    return final_frame

def generate_dataset(n: int,
                     max_range: int | float,
                     spacing: int | float,
                     disc_radius: int | float,
                     x_range: tuple[int, int] | tuple[float, float] | list[int | float],
                     y_range: tuple[int, int] | tuple[float, float] | list[int | float],
                     normal_center: tuple[float | int, float | int],
                     standard_deviation: tuple[float | int, float | int],
                     dataset_name: str,
                     file_extension: Literal[".csv"] | Literal[".pkl"],
                     save_location: str | pathlib.Path,
                     visual_config: VisualConfig,
                     weight: list[int | float] | NDArray[Any] | None = None,
                     round_customers: int | None = None,
                     )  -> tuple[pathlib.Path, pathlib.Path]:
    '''
    This function is the main script for generation of the dataset and it's export\n
    Parameters:\n
    - **n**: Number of customers to create \n
    - **max_range**: Max range of the service centers coverage\n
    - **spacing**: Spacing of the service location grid\n
    - **disc_radius**: Radius parameter for the Poisson Disc algorithm\n
    - **x_range**: (min, max) x range of the space where customers and service locations will be generated\n
    - **y_range**: (min, max) y range of the space where customers and service locations will be generated\n
    - **normal_center**: (customer, service) Center (mean) for normal random generation of customer demand and service capacity using normal distribution\n
    - **standard_deviation**: (customer, service) Standard deviation for normal random generation of customer demand and service capacity using normal distribution\n
    - **dataset_name**: name (without extension) used in the creation of the saved files and displayed in the plot\n
    - **file_extension**: (".csv", ".pkl") save file extension\n
    - **save_location**: (only the directory) save location for the exported files\n
    - **visual_config**: (VisualConfig class) setting for the matplotlib visualisation\n
    - **weight**: Vector of weights for the service locations, if None is provided weights of 1 will be used\n
    - **round_customers**: Rounds the customer location to the given number of decimal places, if None is provided there will be no rounding\n
    ___
    - **returns:** Service dataset path, customer dataset path
    '''
    
    service_centers = service_location_grid_generation(spacing=spacing, x_range=x_range, y_range=y_range)
    customers = poisson_disc_random_samples(n_points=n, radius=disc_radius, x_range=x_range, y_range=y_range)
    
    if round_customers is not None:
        customers = np.round(customers, decimals=round_customers)
    
    customer_demand = customer_demand_generation(len(customers), center=normal_center[0], deviation=standard_deviation[0])
    service_capacity = service_capacity_generation(len(service_centers), center=normal_center[1], deviation=standard_deviation[1])
    
    # print(f"{customers.shape = }")
    # print(f"{service_centers.shape = }")
    
    if weight is None:
        service_weight = [1] * len(service_centers)
    else:
        service_weight = weight[:len(service_centers) + 1]    
        
    service_frame = create_location_dataframe(locations=service_centers, capacity=service_capacity, weight=service_weight, max_range=max_range)
    customer_frame = create_location_dataframe(locations=customers, capacity=customer_demand)
    
    # print(service_frame)
    # print(customer_frame)
    
    # exit()
    fig_no_range, _ = initial_dataset_display(customers=customers,
                            services=service_centers,
                            max_range=max_range,
                            x_range=x_range,
                            y_range=y_range,
                            colors=visual_config.colors,
                            alphas=visual_config.alphas,
                            markers=visual_config.markers,
                            title=dataset_name,
                            toggle_ranges=False)
    fig_range, _ = initial_dataset_display(customers=customers,
                            services=service_centers,
                            max_range=max_range,
                            x_range=x_range,
                            y_range=y_range,
                            colors=visual_config.colors,
                            alphas=visual_config.alphas,
                            markers=visual_config.markers,
                            title=dataset_name,
                            toggle_ranges=True)
    
    
    full_location = f"{save_location}/{dataset_name}"
    service_path = f"{full_location}_service{file_extension}"
    customer_path = f"{full_location}_customers{file_extension}"
    
    data_save(service_frame, file_type=file_extension, location=service_path)
    data_save(customer_frame, file_type=file_extension, location=customer_path)
    fig_no_range.savefig(f"{save_location}/{dataset_name}_no_range.png")
    fig_range.savefig(f"{save_location}/{dataset_name}_range.png")
    
    return (pathlib.Path(service_path), pathlib.Path(customer_path))
        

if __name__ == "__main__":
    pass

    visualSettings = VisualConfig()
    
    generate_dataset(# n=50,
                     # n=150,
                     n = 5,
                     max_range=30,
                     spacing=20,
                     disc_radius=5,
                     x_range=(0, 100),
                     y_range=(0, 100),
                     normal_center=(300, 3500),
                     standard_deviation=(80, 100),
                     dataset_name="test_dataset_3_smallest",
                     file_extension=".csv",
                     save_location="./src/tools/tmp",
                     visual_config=visualSettings,
                     weight=None,
                     round_customers=0)
