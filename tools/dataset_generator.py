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

from dataset_visualisation import initial_dataset_display


def poisson_disc_random_samples(n_points: int,
                                radius: int | float,
                                x_range: tuple[int, int] | list[int],
                                y_range: tuple[int, int] | list[int],) -> NDArray[np.float64]:
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
    
def service_location_grid_generation(spacing: int,
                                     x_range: tuple[int, int] | list[int],
                                     y_range: tuple[int, int] | list[int],) -> NDArray[Any]:
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

def generate_dataset() -> None:
    '''
    This function is the main script for generation of the dataset and it's export
    '''
    

if __name__ == "__main__":
    pass

    n = 250
    x_range = (0, 100)
    y_range = (0, 100)
    r = 3
    spacing = 20
    max_range = 30
    
    service_centers = service_location_grid_generation(spacing=spacing, x_range=x_range, y_range=y_range)
    customers = poisson_disc_random_samples(n_points=n, radius=r, x_range=x_range, y_range=y_range)
    customers = np.round(customers)
    
    customer_demand = customer_demand_generation(len(customers), center=300, deviation=80)
    service_capacity = service_capacity_generation(len(service_centers), center=500, deviation=90)
    
    print(f"{customers.shape = }")
    print(f"{service_centers.shape = }")
    
    service_weight = [1] * len(service_centers)
    service_frame = create_location_dataframe(locations=service_centers, capacity=service_capacity, weight=service_weight, max_range=max_range)
    customer_frame = create_location_dataframe(locations=customers, capacity=customer_demand)
    
    # print(service_frame)
    # print(customer_frame)
    
    # exit()
    initial_dataset_display(customers=customers,
                            services=service_centers,
                            max_range=max_range,
                            x_range=x_range,
                            y_range=y_range,
                            colors=("blue", "red"),
                            alphas=(0.7, 0.5),
                            markers=(".", "+"),
                            title="Dataset generation boogaloo",
                            toggle_ranges=False)
    
    data_save(service_frame, file_type=".csv", location="./tools/tmp/service_test_1.csv")
    data_save(customer_frame, file_type=".csv", location="./tools/tmp/customer_test_1.csv")