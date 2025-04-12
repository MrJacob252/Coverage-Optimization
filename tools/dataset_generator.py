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
                               demand_range: tuple[int | float, int | float] | list [int | float]) -> NDArray[Any]:
    '''
    Function generates random demand value for "n_location" customers in range specified by the "demand_range" parameter
    '''
    
    # TODO:
    
    return np.array([0, 0])

def service_capacity_generation(n_locations: int,
                                demand_range: tuple[int | float, int | float] | list [int | float]) -> NDArray[Any]:
    '''
    Function generates random capacity for each "n_locations" service centers in range specified by the "service_range"
    '''
        
    # TODO:
    
    return np.array([0, 0])

def data_save(data: pd.DataFrame,
              type: Literal[".csv", ".pkl"],
              location: str | pathlib.Path) -> None:
    '''
    Function saves the data into either .csv or .pkl (specified by the "type" parameter) onto a location 
    specified by the "location" and "file name" parameter.
    '''
    
    # TODO:
    
def create_location_dataframe(locations: NDArray[Any],
                              capacity: NDArray[Any],
                              max_range: int | float | None = None) -> pd.DataFrame:
    '''
    Function merges the locations coordinates and capacity/demand values into one DataFrame with 3/4 columns\n
    **X**: x coordinate of the location\n
    **Y**: y coordinate of the location\n
    **Value**: Value of the demand/capacity of the location\n
    **Range**: Value of the range of the service location caved only on row 0 and only for service location
    '''
    
    # TODO:
    
    return pd.DataFrame()

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
    
    print(f"{customers.shape = }")
    print(f"{service_centers.shape = }")
    
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